#!/usr/bin/env python

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
from serial_data_parser import SerialDataParser
from motor_temperature_reader import MotorTemperatureReader
from gps_reader import GpsReader

MESSAGE_LENGTH = 220
INTERVAL_SEC = 0.4
TIMEOUT = 4
MESSAGES_IN_QUEUE_LIMIT = 10

NUMBER_OF_MESSAGES_TO_RESEND = 4
SEND_TO_BOARD_COMPUTER = False
SEND_TO_STRATEGY = True
COLLECT_SERIAL_DATA = True
COLLECT_MOTOR_TEMPERATURE = True
COLLECT_GPS_DATA = True

LOG_PATH = "logs.log"
BACKUP_PATH = "backup.bin"

URI_BOARD_COMPUTER = "ws://192.168.43.117:55201/api/websocket" # TODO make it work with static ip
URI_STRATEGY = "wss://lst-api-v1.azurewebsites.net/api/WebSocket"

ssl_context = ssl.create_default_context()

backup_handler = BackupHandler(BACKUP_PATH, MESSAGE_LENGTH)
car = Car()


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
                        await websocket.send(message)
                        print("sent")
                        messages_to_resend = backup_handler.get_unsent_messages(NUMBER_OF_MESSAGES_TO_RESEND)

                        for msg in messages_to_resend:
                            await websocket.send(msg)
                            messages_to_resend.remove(msg)
            else:
                async with WebSocketConnectWithTimeout(url, connect_timeout=TIMEOUT) as websocket:
                    while True:
                        message = await q.get()
                        q.task_done()
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
    return car.to_bytes()

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
    can_interface = 'can0'
    print("CAN interface:",can_interface)
    bus = can.interface.Bus(can_interface, bustype='socketcan_native')
    print("BUS:",bus)
    frames = Frames()
    start_time = time.time()
    finalMessage = bytearray(MESSAGE_LENGTH)

    while True:
        message = bus.recv()
        # START for testing
        # arbitration_id = 11  # int(input("ID: "))
        # dat = [1, 16, 3, 4, 5, 6, 1, 8]
        # dat = dat[0: 8]

        # message = can.Message(arbitration_id=arbitration_id,
        #                       data=dat, extended_id=False)
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

    s = SerialDataParser(car.Battery.Cells.voltages, car.Battery.Cells.temperatures)
    m = MotorTemperatureReader(car.General.motorTemperature)
    g = GpsReader(car.Gps)

    tasks = []
    if SEND_TO_BOARD_COMPUTER:
        tasks.append(asyncio.create_task(
            send_message(queue_board_computer, URI_BOARD_COMPUTER)
        ))
    if SEND_TO_STRATEGY:
        tasks.append(asyncio.create_task(
            send_message(queue_cloud, URI_STRATEGY)
        ))
    if COLLECT_SERIAL_DATA:
        tasks.append(asyncio.create_task(s.start_listening()))
    if COLLECT_MOTOR_TEMPERATURE:
        tasks.append(asyncio.create_task(m.start_listening()))
    if COLLECT_GPS_DATA:
        tasks.append(asyncio.create_task(g.start_listening()))

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
