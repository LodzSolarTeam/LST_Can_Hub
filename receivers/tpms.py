from enum import Enum
from struct import unpack
from car import Car
from bluepy.btle import Scanner
import can


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
        bus = can.Bus(interface='socketcan_ctypes',
                      channel='vcan0')

        data = list(self._pressure.values())

        message = can.Message(arbitration_id=123,
                              is_extended_id=False,
                              data=data)

        bus.send(message, timeout=0.2)

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

        pressure = unpacked[2] / 1000 # kPa
        temperature = unpacked[3] / 100 # C
        # battery = unpacked[4]

        return (pressure, temperature)

    def run(self):
        print("Starting...")
        while True:
            devices = self._scan_devices()

            for wheel, data in devices.items():
                manufacturer_data = self._get_manufacturer_data(data)

                if manufacturer_data == None:
                    continue

                pressure, temperature = self._decode_data(manufacturer_data)

                self._pressures[wheel] = int(pressure)
                self._temperatures[wheel] = int(temperature)

                print(wheel, pressure, temperature)

            self._send_to_can()
            self._fill_car()
