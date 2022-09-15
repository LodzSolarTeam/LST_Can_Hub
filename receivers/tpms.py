from enum import Enum
import logging
from struct import unpack
import struct
from car import Car
from bluepy.btle import Scanner
import can
from receivers.e2_can import CAN_INTERFACE


class Wheel(Enum):
    FRONT_LEFT = 1
    FRONT_RIGHT = 2
    REAR_LEFT = 3
    REAR_RIGHT = 4


DEVICE_DICT = {
    '80:ea:ca:10:06:7d': Wheel.FRONT_LEFT,
    '81:ea:ca:20:06:55': Wheel.FRONT_RIGHT,
    '82:ea:ca:30:04:0e': Wheel.REAR_LEFT,
    '83:ea:ca:40:03:2e': Wheel.REAR_RIGHT,
}


def tpms_receiver(car: Car):
    TPMSReceiver(car).run()


class TPMSReceiver:
    def __init__(self, car: Car) -> None:
        logging.info("Initializing.")

        self._car = car
        self._scanner = Scanner()

        self._pressures = {
            Wheel.FRONT_LEFT: 0,
            Wheel.FRONT_RIGHT: 0,
            Wheel.REAR_LEFT: 0,
            Wheel.REAR_RIGHT: 0,
        }

        self._temperatures = {
            Wheel.FRONT_LEFT: 0,
            Wheel.FRONT_RIGHT: 0,
            Wheel.REAR_LEFT: 0,
            Wheel.REAR_RIGHT: 0,
        }

    def _scan_devices(self):
        result = {}
        # scanning will be performed every 1 second
        devices = self._scanner.scan(timeout=1)

        for dev in devices:
            if dev.addr in DEVICE_DICT:
                result[DEVICE_DICT[dev.addr]] = dev.getScanData()

        return result

    def _send_to_can(self):
        with can.interface.Bus(CAN_INTERFACE, bustype='socketcan') as bus:

            data = struct.pack('HHHH',
                               int(self._pressures[Wheel.FRONT_LEFT]),
                               int(self._pressures[Wheel.FRONT_RIGHT]),
                               int(self._pressures[Wheel.REAR_LEFT]),
                               int(self._pressures[Wheel.REAR_RIGHT]))

            message = can.Message(arbitration_id=123, data=data)

            try:
                bus.send(message)
                logging.info(f"Message sent on {bus.channel_info}")
            except can.CanError as e:
                logging.warn(f"Cannot send message {e}")

    def _fill_car(self):
        self._car.fill_tire_data(list(self._pressures.values()), list(self._temperatures.values()))

    def _get_manufacturer_data(self, device_data):
        for data in device_data:
            if data[1] == "Manufacturer":
                return data[2]

        return None

    def _decode_data(self, data: str):
        # source: https://github.com/ra6070/BLE-TPMS
        unpacked = unpack("HIIIBB", bytes.fromhex(data))

        pressure = unpacked[2] / 10000  # bars * 10
        temperature = unpacked[3] / 100  # C
        battery = unpacked[4]

        return (pressure, temperature, battery)

    def run(self):
        logging.info("Starting.")
        while True:
            devices = self._scan_devices()

            data_changed = False

            for wheel, data in devices.items():
                manufacturer_data = self._get_manufacturer_data(data)

                if manufacturer_data == None:
                    logging.warn("No manufacturer data.")
                    continue

                pressure, temperature, battery = self._decode_data(manufacturer_data)

                self._pressures[wheel] = int(pressure)
                self._temperatures[wheel] = int(temperature)

                logging.info(f"{wheel} pressure: {pressure} temperature: {temperature} battery: {battery}")
                data_changed = True

            if data_changed:
                self._fill_car()
                self._send_to_can()
