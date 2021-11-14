from datahub.bytejoin import bytejoin

class BatteryWarnings:
    def __init__(self):
        self.warnings = bytearray(3)
        
    def to_bytes(self):
        return bytejoin(self)