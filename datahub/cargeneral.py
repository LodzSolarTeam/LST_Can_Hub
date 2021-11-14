from datahub.bytejoin import bytejoin

class CarGeneral:
    def __init__(self):
        self.timestamp = bytearray(8)
        self.throttlePosition = bytearray(1)
        self.motorController = bytearray(1)
        self.regenerationBrake = bytearray(1)
        self.cruiseThrottle = bytearray(1)
        self.cruiseDesiredSpeed = bytearray(1)
        self.batteryError = bytearray(1)
        self.engineError = bytearray(1)
        self.driveMode = bytearray(1)
        self.cruiseEngaged = bytearray(1)
        self.horn = bytearray(1)
        self.handBrake = bytearray(1)
        self.temperatures = bytearray(4)
        self.rpm = bytearray(2)
        self.solarRadiance = bytearray(2)
        self.motorTemperature = bytearray(2)
        
    def to_bytes(self):
        return bytejoin(self)