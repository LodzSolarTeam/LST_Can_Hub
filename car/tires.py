from car.utils import bytejoin


class Tires:
    def __init__(self):
        self.pressures = bytearray(4)
        self.tiresTemperatures = bytearray(4)

    def reset(self):
        pass

    def to_bytes(self):
        return bytejoin(self)

    def from_bytes(self, bytes):
        self.pressures = bytes[0:4]
        self.tiresTemperatures = bytes[4:8]

    def save_cache(self):
        open("tires.cache", "wb").write(self.to_bytes())

    def load_cache(self):
        try:
            self.from_bytes(open("tires.cache", "rb").read())
        except FileNotFoundError:
            pass
