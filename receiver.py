#!/usr/bin/env python

# Co zrobic, zeby telemetria byla wysylana:
# Wlaczyc hotspota z  internetem:
# Nazwa: 4DS612
# Haslo: mTzW4snd
# Wlaczyc Raspberke i podlaczyc CAN do shielda
# Telemetria powinna zaczac sie wysylac  po ok. 5 sekundach. Skrypt zbierajacy dane powinien automatycznie odpalic sie po wlaczeniu Raspberki. Dane mozemy zobaczyc:
# Czyste dane: https://lst-api-v1.azurewebsites.net/api/car/recent
# Frontend: https://white-sky-0251a6303.azurestaticapps.net
# Jesli wszystko dziala poprawnie to powinnismy na 'czyste dane' miec aktualny timestamp
# Dane z CAN sa wysylane co 3 sekundy do backendu na chmurze.

# Skypt, ktory odpala sie przy starcie Raspberry
#   /etc/init.d/can_ [I calej nazwy pliku niestety nie pamietam, trzeba sprawdzic]
# zeby wylaczyc automatyczne odpalanie sie skryptu przy starcie:
#   sudo update-rc.d can_ [To ten sam plik co wyzej, trzeba sprawdzic cala nazwe] remove

# Jakby bylo potrzeba to do dane logowania do RPi3 (nie musimy tego robic jak tylko chcemy wlaczyc telemetrie):
# Username: pi
# Password: raspberry

"""
Commands to start collecting data:

sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
python3 receiver.py
"""
from asyncio.futures import CancelledError
import can
import asyncio
from can import message
import websockets
import time
import logging
import ssl

from backup_handler import BackupHandler
from car import Car
from frames import Frames

MESSAGE_LENGTH = 213
INTERVAL_SEC = 0.4
TIMEOUT = 4
MESSAGES_IN_QUEUE_LIMIT = 10
SEND_TO_BOARD_COMPUTER = False
SEND_TO_STRATEGY = True

LOG_PATH = "/home/pi/lst_canhub_py/logs.log"
BACKUP_PATH = "/home/pi/lst_canhub_py/backup.bin"

URI_BOARD_COMPUTER = "ws://localhost:55201/api/websocket" # TODO make it work with static ip
URI_STRATEGY = "wss://lst-api-v1.azurewebsites.net/api/WebSocket"

ssl_context = ssl.create_default_context()

backup_handler = BackupHandler(BACKUP_PATH, MESSAGE_LENGTH)


class WebSocketConnectWithTimeout(websockets.connect):
    def __init__(self, *args, **kwargs):
        self.connect_timeout = kwargs.pop('connect_timeout')
        super(WebSocketConnectWithTimeout, self).__init__(*args, **kwargs)

    async def __aenter__(self, *args, **kwargs):
        return await asyncio.wait_for(super(WebSocketConnectWithTimeout, self).__aenter__(*args, **kwargs), timeout=self.connect_timeout)

    async def __aexit__(self, *args, **kwargs):
        return await super(WebSocketConnectWithTimeout, self).__aexit__(*args, **kwargs)


async def send_message(q, url):
    logging.debug(f"Start messages coroutine for {url}")
    message = b""
    messages_to_resend = []

    while True:
        try:
            if url[0:3] == "wss":
                async with WebSocketConnectWithTimeout(url, ssl=ssl_context, connect_timeout=TIMEOUT) as websocket:
                    while True:
                        message = await q.get()
                        q.task_done()
                        print("wss size" + str(q.qsize()))
                        await websocket.send(message)
                        message = b""

                        messages_to_resend = backup_handler.get_unsent_messages(3) # TODO

                        for msg in messages_to_resend:
                            await websocket.send(msg)
                            messages_to_resend.remove(msg)
            else:
                async with WebSocketConnectWithTimeout(url, connect_timeout=TIMEOUT) as websocket:
                    while True:
                        message = await q.get()
                        q.task_done()
                        print("ws size" + str(q.qsize()))
                        await websocket.send(message)
                        message = b""

        except CancelledError:
            raise
        except Exception as e:
            logging.warning(f"Failed sending msg to " + url + ": " +
                            str(type(e).__name__) + ". Saving message to the backup file.")
            if message:
                backup_handler.backup_messages([message])
            if messages_to_resend:
                backup_handler.backup_messages(messages_to_resend)
            await asyncio.sleep(0.2)


def create_final_message(car):
    return car.timestamp+car.throttlePosition+car.motorController+car.regenerationBrake+car.cruiseThrottle + \
        car.cruiseDesiredSpeed+car.batteryError+car.engineError+car.driveMode+car.cruiseEngaged+car.horn + \
        car.handBrake+car.temperatures+car.rpm+car.solarRadiance + \
        car.remainingChargeTime + \
        car.chargerEnabled+car.systemState+car.inputOutputState+car.packCRate+car.stateOfCharge + \
        car.stateOfHealth+car.numberOfCellsConnected+car.remainingEnergy+car.deviationOfVoltageInCells + \
        car.packTemperatureMax+car.LMUNumberWithMaxTemperature+car.packTemperatureMin + \
        car.LMUNumberWithMinTemperature+car.cellVoltageMax+car.cellNumberWithMaxVoltage+car.cellVoltageMin + \
        car.cellNumberWithMinVoltage+car.cellAvgVoltage+car.packVoltage+car.packCurrent+car.warnings + \
        car.errors + \
        car.stopLights+car.lowBeamLights+car.highBeamLights+car.rightIndicatorLights + \
        car.leftIndicatorLights+car.parkLights+car.interiorLights+car.emergencyLights+car.mpptInputVoltage + \
        car.mpptInputCurrent+car.mpptOutputVoltage + \
        car.mpptOutputPower+car.mpptPcbTemperature+car.mpptMofsetTemperature+car.pressures + \
        car.tiresTemperatures+car.dateDay+car.dateMonth+car.dateYear+car.timeHour+car.timeMin + \
        car.timeSec+car.latitude+car.latitudeDirection+car.longitude+car.longitudeDirection + \
        car.altitude+car.speedKnots+car.speedKilometers+car.satellitesNumber+car.quality


async def queue_message(q, finalMessage):
    try:
        if q.qsize() > MESSAGES_IN_QUEUE_LIMIT:
            logging.warning(
                f"Too much unprocessed messages, saving {MESSAGES_IN_QUEUE_LIMIT} messages to a file")
            messages = []
            for _ in range(MESSAGES_IN_QUEUE_LIMIT):
                message = await q.get()
                q.task_done()
                messages.append(message)
            backup_handler.backup_messages(messages)

        await q.put(finalMessage)
    except Exception as e:
        logging.warning(f"Error queueing message: " + str(e))


async def can_producer(queue_board_computer, queue_cloud):
    logging.info("Configuring Can")
    # can_interface = 'can0'
    # bus = can.interface.Bus(can_interface, bustype='socketcan_native')

    frames = Frames()
    start_time = time.time()
    finalMessage = bytearray(MESSAGE_LENGTH)
    car = Car()

    while True:
        # message = bus.recv()
        # START for testing
        arbitration_id = 11  # int(input("ID: "))
        dat = [1, 16, 3, 4, 5, 6, 1, 8]
        dat = dat[0: 8]

        message = can.Message(arbitration_id=arbitration_id,
                              data=dat, extended_id=False)
        # END for testing

        frames.save_frame(message.arbitration_id, message.data)
        await asyncio.sleep(0)

        if time.time() - start_time > INTERVAL_SEC:
            start_time = time.time()
            try:
                car.fill_car_model(message.timestamp, frames)
                finalMessage = create_final_message(car)
            except Exception as e:
                logging.warning(f"Failed creating final message: " + str(e))
            if SEND_TO_STRATEGY:
                await queue_message(queue_cloud, finalMessage)
                await asyncio.sleep(0)
            if SEND_TO_BOARD_COMPUTER:
                await queue_message(queue_board_computer, finalMessage)
                await asyncio.sleep(0)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ]
    )


async def main():
    setup_logging()

    logging.info("Start event loop")
    queue_board_computer = asyncio.Queue()
    queue_cloud = asyncio.Queue()
    tasks = []
    if SEND_TO_BOARD_COMPUTER:
        consumer_task_1 = asyncio.create_task(
            send_message(queue_board_computer, URI_BOARD_COMPUTER)
        )
        tasks.append(consumer_task_1)
    if SEND_TO_STRATEGY:
        consumer_task_2 = asyncio.create_task(
            send_message(queue_cloud, URI_STRATEGY)
        )
        tasks.append(consumer_task_2)
    producer_task = asyncio.create_task(
        can_producer(queue_board_computer, queue_cloud)
    )
    tasks.append(producer_task)

    await asyncio.wait(
        tasks,
        return_when=asyncio.ALL_COMPLETED
    )


if __name__ == "__main__":
    asyncio.run(main())
