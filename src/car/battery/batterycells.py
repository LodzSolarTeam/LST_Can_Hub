from src.car.utils import bytejoin


class BatteryCells:
    def __init__(self):
        self.voltages = bytearray(64)
        self.temperatures = bytearray(16)

    def reset(self):
        self.voltages = bytearray(64)
        self.temperatures = bytearray(16)
        pass

    def to_bytes(self):
        return bytejoin(self)
