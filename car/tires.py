from car.utils import bytejoin


class Tires:
    def __init__(self):
        self.pressures = bytearray(4)
        self.tiresTemperatures = bytearray(4)

    def reset(self):
        pass

    def to_bytes(self):
        return bytejoin(self)
