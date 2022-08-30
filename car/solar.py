from car.utils import bytejoin


class Solar:
    def __init__(self):
        self.mpptInputVoltage = bytearray(16)
        self.mpptInputCurrent = bytearray(16)
        self.mpptOutputVoltage = bytearray(16)
        self.mpptOutputPower = bytearray(16)
        self.mpptPcbTemperature = bytearray(8)
        self.mpptMofsetTemperature = bytearray(8)

    def reset(self):
        pass

    def to_bytes(self):
        return bytejoin(self)
