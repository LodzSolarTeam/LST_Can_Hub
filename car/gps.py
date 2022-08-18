from car.utils import bytejoin


class Gps:
    def __init__(self):
        self.latitude = bytearray(8)
        self.latitudeDirection = bytearray(1)
        self.longitude = bytearray(8)
        self.longitudeDirection = bytearray(1)
        self.altitude = bytearray(8)
        self.speedKnots = bytearray(8)
        self.speedKilometers = bytearray(8)
        self.satellitesNumber = bytearray(1)
        self.quality = bytearray(1)

    def to_bytes(self):
        return bytejoin(self)
