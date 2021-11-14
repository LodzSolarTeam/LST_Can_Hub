from datahub.bytejoin import bytejoin

class Lights:
    def __init__(self):
        self.stopLights = bytearray(1)
        self.lowBeamLights = bytearray(1)
        self.highBeamLights = bytearray(1)
        self.rightIndicatorLights = bytearray(1)
        self.leftIndicatorLights = bytearray(1)
        self.parkLights = bytearray(1)
        self.interiorLights = bytearray(1)
        self.emergencyLights = bytearray(1)
        
    def to_bytes(self):
        return bytejoin(self)