from enum import Enum
import can


class Wheel(Enum):
    FRONT_LEFT = 1
    FRONT_RIGHT = 2
    REAR_LEFT = 3
    REAR_RIGHT = 4


class TPMSCanSender:
    def __init__(self):
        self._pressure = {
            Wheel.FRONT_LEFT: 0,
            Wheel.FRONT_RIGHT: 0,
            Wheel.REAR_LEFT: 0,
            Wheel.REAR_RIGHT: 0,
        }

    def set_pressure(self, wheel: Wheel, pressure: int):
        self._pressure[wheel] = pressure
        # print(self._pressure)

    def send(self):
        bus = can.Bus(interface='socketcan_ctypes',
                      channel='vcan0')

        data = list(self._pressure.values())

        message = can.Message(arbitration_id=123,
                              is_extended_id=False,
                              data=data)

        bus.send(message, timeout=0.2)
