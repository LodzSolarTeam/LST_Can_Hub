"""
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
python3 receiver.py -u ws://192.168.43.117:55201/api/WebSocket
"""
import can
import asyncio
import websockets
import time
import sys
import threading
import functools
import argparse
import logging

from struct import pack
from datetime import datetime
from concurrent import futures


MESSAGE_LENGTH = 213
INTERVAL_SEC = 3
URI = None
# DEFAULT_URI = "ws://192.168.43.117:55201/api/WebSocket"
DEFAULT_URI = "ws://localhost:55201/api/WebSocket"
LOG_PATH = "./logs.log"
BACKUP_PATH = "./backup.bin"

sent_threads = []


class Frames:
    # CORE CAN:
    engines = bytearray(5)
    lights = bytearray(2)
    batteryMainFrame = bytearray(8)
    speed = bytearray(8)
    sunSensor = bytearray(8)
    # CAN 4
    errorFrame = bytearray(8)
    batteryVoltageCellsFrame = bytearray(8)
    batteryErrorFrame = bytearray(8)
    # Change  batteryTemperatureFrame = bytearray(5)
    batteryTemperatureFrame = bytearray(4)
    batteryRemainingEnergyFrame = bytearray(5)
    batteryOtherDataFrame = bytearray(8)
    # Change chargerFrame = bytearray(8)
    chargerFrame = bytearray(5)
    chargeControllerFrame = bytearray(5)
    mppt1Input = bytearray(8)
    mppt1Output = bytearray(8)
    mppt1TemperatureData = bytearray(8)
    mppt2Input = bytearray(8)
    mppt2Output = bytearray(8)
    mppt2TemperatureData = bytearray(8)
    mppt3Input = bytearray(8)
    mppt3Output = bytearray(8)
    mppt3TemperatureData = bytearray(8)
    mppt4Input = bytearray(8)
    mppt4Output = bytearray(8)
    mppt4TemperatureData = bytearray(8)


class Car:
    # GENERAL
    timestamp = bytearray(8)
    throttlePosition = bytearray(1)
    motorController = bytearray(1)
    regenerationBrake = bytearray(1)
    cruiseThrottle = bytearray(1)
    cruiseDesiredSpeed = bytearray(1)
    batteryError = bytearray(1)
    engineError = bytearray(1)
    driveMode = bytearray(1)
    cruiseEngaged = bytearray(1)
    horn = bytearray(1)
    handBrake = bytearray(1)
    temperatures = bytearray(4)
    rpm = bytearray(2)
    solarRadiance = bytearray(2)
    # Battery
    remainingChargeTime = bytearray(4)
    chargerEnabled = bytearray(1)
    systemState = bytearray(1)
    inputOutputState = bytearray(1)
    packCRate = bytearray(2)
    stateOfCharge = bytearray(1)
    stateOfHealth = bytearray(1)
    numberOfCellsConnected = bytearray(1)
    remainingEnergy = bytearray(2)
    deviationOfVoltageInCells = bytearray(2)
    packTemperatureMax = bytearray(1)
    LMUNumberWithMaxTemperature = bytearray(1)
    packTemperatureMin = bytearray(1)
    LMUNumberWithMinTemperature = bytearray(1)
    cellVoltageMax = bytearray(2)
    cellNumberWithMaxVoltage = bytearray(1)
    cellVoltageMin = bytearray(2)
    cellNumberWithMinVoltage = bytearray(1)
    cellAvgVoltage = bytearray(2)
    packVoltage = bytearray(2)
    packCurrent = bytearray(2)
    warnings = bytearray(3)  # BatteryWarnings = 3 bajty
    errors = bytearray(4)  # BatteryErrors = 4 bajty
    # LIGHTS
    stopLights = bytearray(1)
    lowBeamLights = bytearray(1)
    highBeamLights = bytearray(1)
    rightIndicatorLights = bytearray(1)
    leftIndicatorLights = bytearray(1)
    parkLights = bytearray(1)
    interiorLights = bytearray(1)
    emergencyLights = bytearray(1)
    # SOLAR
    mpptInputVoltage = bytearray(16)  # MpptAmount = 4 uint = 4 bajty
    mpptInputCurrent = bytearray(16)
    mpptOutputVoltage = bytearray(16)
    mpptOutputPower = bytearray(16)
    mpptPcbTemperature = bytearray(8)  # short = 2 bajty
    mpptMofsetTemperature = bytearray(8)
    # TIRES
    pressures = bytearray(4)  # tiresPressureSize = 4
    tiresTemperatures = bytearray(4)  # tiresTemperaturesSize = 4
    # GPS
    dateDay = bytearray(1)
    dateMonth = bytearray(1)
    dateYear = bytearray(2)
    timeHour = bytearray(1)
    timeMin = bytearray(1)
    timeSec = bytearray(1)
    latitude = bytearray(8)  # double
    latitudeDirection = bytearray(1)
    longitude = bytearray(8)  # double
    longitudeDirection = bytearray(1)
    altitude = bytearray(8)  # double
    speedKnots = bytearray(8)  # double
    speedKilometers = bytearray(8)  # double
    satellitesNumber = bytearray(1)
    quality = bytearray(1)


class BackupFile:
    @staticmethod
    def write_into_binary_file(path, data):
        try:
            with open(path, "ab") as f:
                f.write(data)
                f.write(b"\n")
        except Exception as e:
            logging.warning("Failed to save message to the file" + str(e))

    @staticmethod
    def read_from_binary_file(path):
        with open(path, "ab") as f:
            data = f.read()
            logging.info(data)

    @staticmethod
    def get_timestamp(path, message_number, message_length):
        with open(path, "ab") as f:
            timestamp = bytearray(8)
            f.seek(message_number*message_length, 0)
            timestamp = f.read(8)

        return timestamp


def byte_to_bit_array(byte):
    bit_string = ''.join(format(ord(byte), '08b'))
    bits = list(map(int, bit_string))
    return bytearray(bits[::-1])


async def send_message(message):
    logging.debug("Start sending message")
    async with websockets.connect(URI) as websocket:
        await websocket.send(message)
        # FIN change to debug
        logging.info("Message sent")


def parse_car_timestamp(timestamp):
    # for tests: 1559297416.090523
    date = datetime.fromtimestamp(timestamp)
    int_timestamp = round((date - datetime(1970, 1, 1)).total_seconds())
    return pack("Q", int_timestamp)


def fill_car_model(car, timestamp, frames):
    try:
        car.timestamp = parse_car_timestamp(timestamp)
    except Exception as err:
        logging.warning(f"Timestamp cannot be converted {timestamp}")
        logging.warning(err)
        logging.warning("Skipping frame")
        return car

    # GENERAL
    car.throttlePosition = frames.engines[0:1]
    car.motorController = frames.engines[1:2]
    byte_to_bit_array(car.motorController)
    car.regenerationBrake = frames.engines[2:3]
    car.cruiseThrottle = frames.engines[3:4]
    car.cruiseDesiredSpeed = frames.engines[4:5]
    car.batteryError = byte_to_bit_array(frames.lights[1:2])[1:2]
    car.engineError = byte_to_bit_array(frames.lights[1:2])[2:3]
    driveMode = byte_to_bit_array(frames.lights[1:2])
    car.driveMode = (driveMode[4]*2 + driveMode[5]).to_bytes(1, "big")
    car.cruiseEngaged = byte_to_bit_array(frames.lights[1:2])[6:7]
    car.horn = byte_to_bit_array(frames.lights[0:1])[7:8]
    car.handBrake = byte_to_bit_array(frames.lights[1:2])[0:1]
    # car.temperatures # not exisiting
    car.rpm = frames.speed[0:2]
    car.solarRadiance = frames.sunSensor[0:2]
    # BATTERY
    # TODO check
    car.remainingChargeTime = frames.batteryRemainingEnergyFrame[0:3]
    car.remainingChargeTime.append(0x00)
    car.chargerEnabled = frames.batteryMainFrame[6:7]
    car.systemState = frames.batteryMainFrame[4:5]
    car.inputOutputState = frames.batteryOtherDataFrame[4:5]
    car.packCRate = frames.batteryOtherDataFrame[5:7][::-1]
    car.stateOfCharge = frames.batteryMainFrame[5:6]
    car.stateOfHealth = frames.batteryOtherDataFrame[0:1]
    car.numberOfCellsConnected = frames.batteryOtherDataFrame[1:2]
    car.remainingEnergy = frames.batteryRemainingEnergyFrame[3:5][::-1]
    car.deviationOfVoltageInCells = frames.batteryOtherDataFrame[2:4][::-1]
    car.packTemperatureMax = frames.batteryTemperatureFrame[0:1]
    car.LMUNumberWithMaxTemperature = frames.batteryTemperatureFrame[1:2]
    car.packTemperatureMin = frames.batteryTemperatureFrame[2:3]
    car.LMUNumberWithMinTemperature = frames.batteryTemperatureFrame[3:4]
    car.cellVoltageMax = frames.batteryVoltageCellsFrame[6:8][::-1]
    car.cellNumberWithMaxVoltage = frames.batteryVoltageCellsFrame[5:6]
    car.cellVoltageMin = frames.batteryVoltageCellsFrame[3:5][::-1]
    car.cellNumberWithMinVoltage = frames.batteryVoltageCellsFrame[2:3]
    car.cellAvgVoltage = frames.batteryVoltageCellsFrame[0:2][::-1]
    car.packVoltage = frames.batteryMainFrame[0:2][::-1]
    car.packCurrent = frames.batteryMainFrame[2:4][::-1]
    car.warnings = frames.batteryErrorFrame[4:7]
    car.errors = frames.batteryErrorFrame[0:4]
    # LIGHTS
    car.stopLights = byte_to_bit_array(frames.lights[0:1])[0:1]
    car.lowBeamLights = byte_to_bit_array(frames.lights[0:1])[1:2]
    car.highBeamLights = byte_to_bit_array(frames.lights[0:1])[2:3]
    car.rightIndicatorLights = byte_to_bit_array(frames.lights[0:1])[3:4]
    car.leftIndicatorLights = byte_to_bit_array(frames.lights[0:1])[4:5]
    car.parkLights = byte_to_bit_array(frames.lights[0:1])[5:6]
    car.interiorLights = byte_to_bit_array(frames.lights[0:1])[5:6]
    car.emergencyLights = byte_to_bit_array(frames.lights[0:1])[6:7]
    # SOLAR
    car.mpptInputVoltage = frames.mppt1Input[4:8] + \
        frames.mppt2Input[4:8] + \
        frames.mppt3Input[4:8] + frames.mppt4Input[4:8]
    car.mpptInputCurrent = frames.mppt1Input[0:4] + \
        frames.mppt2Input[0:4] + \
        frames.mppt3Input[0:4] + frames.mppt4Input[0:4]
    car.mpptOutputVoltage = frames.mppt1Output[0:4] + \
        frames.mppt2Output[0:4] + \
        frames.mppt3Output[0:4] + frames.mppt4Output[0:4]
    car.mpptOutputPower = frames.mppt1Output[4:8] + frames.mppt2Output[4:8] + \
        frames.mppt3Output[4:8] + frames.mppt4Output[4:8]
    car.mpptPcbTemperature = frames.mppt1TemperatureData[6:8] + frames.mppt2TemperatureData[6:8] + \
        frames.mppt3TemperatureData[6:8] + frames.mppt4TemperatureData[6:8]
    car.mpptMofsetTemperature = frames.mppt1TemperatureData[4:6] + frames.mppt2TemperatureData[4:6] + \
        frames.mppt3TemperatureData[4:6]+frames.mppt4TemperatureData[4:6]
    # TIRES not exisiting
    # GPS not exisiting
    return car


def save_frame(frames, id, data):
    if(id == 321):
        frames.engines = data
    elif(id == 770):
        frames.lights = data
    elif(id == 1475):
        frames.batteryMainFrame = data
    elif(id == 1412):
        frames.speed = data
    elif(id == 1029):
        frames.sunSensor = data
    elif(id == 1473):
        frames.batteryVoltageCellsFrame = data
    elif(id == 1474):
        frames.batteryErrorFrame = data
    elif(id == 1476):
        frames.batteryTemperatureFrame = data
    elif(id == 1477):
        frames.batteryRemainingEnergyFrame = data
    elif(id == 1478):
        frames.batteryOtherDataFrame = data
    elif(id == 403105268):
        frames.chargerFrame = data
    elif(id == 31260673):
        frames.chargeControllerFrame = data
    elif(id == 0):
        frames.errorFrame = data
    elif(id == 384):
        frames.mppt1Input = data
    elif(id == 640):
        frames.mppt1Output = data
    elif(id == 1152):
        frames.mppt1TemperatureData = data
    elif(id == 385):
        frames.mppt2Input = data
    elif(id == 641):
        frames.mppt2Output = data
    elif(id == 1153):
        frames.mppt2TemperatureData = data
    elif(id == 386):
        frames.mppt3Input = data
    elif(id == 642):
        frames.mppt3Output = data
    elif(id == 1154):
        frames.mppt3TemperatureData = data
    elif(id == 387):
        frames.mppt4Input = data
    elif(id == 643):
        frames.mppt4Output = data
    elif(id == 1155):
        frames.mppt4TemperatureData = data


def send_message_thread(message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_message(message))
        loop.close()
    except Exception as e:
        logging.warning(f"Failed sending message with exception: " + str(e))
        logging.info("Saving message to the backup file")
        BackupFile.write_into_binary_file(BACKUP_PATH, message)
        loop.close()


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


def create_send_thread(finalMessage):
    try:
        for thread in sent_threads:
            thread.join()
        t = threading.Thread(target=send_message_thread,
                             args=(finalMessage,))
        sent_threads.append(t)
        t.start()
    except Exception as e:
        logging.warning(f"Error creating thread: " + str(e))


async def can_producer():
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
        arbitration_id = int(input("ID: "))
        dat = [1, 16, 3, 4, 5, 6, 1, 8]
        dat = dat[0: 8]

        message = can.Message(arbitration_id=arbitration_id,
                              data=dat, extended_id=False)
        # END for testing

        save_frame(frames, message.arbitration_id, message.data)

        if time.time() - start_time > INTERVAL_SEC:
            start_time = time.time()
            try:
                car = fill_car_model(car, message.timestamp, frames)
                finalMessage = create_final_message(car)
            except Exception as e:
                logging.warning(f"Failed creating final message: " + str(e))
            create_send_thread(finalMessage)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Send car telemetry via websockets")
    parser.add_argument("-u", "--uri", default=DEFAULT_URI, required=False)

    return parser.parse_args()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ]
    )


def main():
    global URI
    args = parse_args()
    URI = args.uri
    setup_logging()

    logging.info("Start event loop")
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(can_producer())


if __name__ == "__main__":
    main()
