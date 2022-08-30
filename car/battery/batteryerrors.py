from car.utils import bytejoin


class BatteryErrors:
    def __init__(self):
        self.errors = bytearray(4)

    def reset(self):
        self.errors = bytearray(4)

    def to_bytes(self):
        return bytejoin(self)
