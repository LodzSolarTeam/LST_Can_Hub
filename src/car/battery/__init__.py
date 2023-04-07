from src.car.battery.batterycells import BatteryCells
from src.car.battery.batteryerrors import BatteryErrors
from src.car.battery.batterywarnings import BatteryWarnings
from src.car.utils import bytejoin


class Battery:
    Warnings = BatteryWarnings()
    Errors = BatteryErrors()
    Cells = BatteryCells()

    def __init__(self):
        self.remainingChargeTime = bytearray(4)
        self.chargerEnabled = bytearray(1)
        self.systemState = bytearray(1)
        self.inputOutputState = bytearray(1)
        self.packCRate = bytearray(2)
        self.stateOfCharge = bytearray(1)
        self.stateOfHealth = bytearray(1)
        self.numberOfCellsConnected = bytearray(1)
        self.remainingEnergy = bytearray(2)
        self.deviationOfVoltageInCells = bytearray(2)
        self.packTemperatureMax = bytearray(1)
        self.LMUNumberWithMaxTemperature = bytearray(1)
        self.packTemperatureMin = bytearray(1)
        self.LMUNumberWithMinTemperature = bytearray(1)
        self.cellVoltageMax = bytearray(2)
        self.cellNumberWithMaxVoltage = bytearray(1)
        self.cellVoltageMin = bytearray(2)
        self.cellNumberWithMinVoltage = bytearray(1)
        self.cellAvgVoltage = bytearray(2)
        self.packVoltage = bytearray(2)
        self.packCurrent = bytearray(2)

    def reset(self):
        self.Warnings.reset()
        self.Errors.reset()
        self.Cells.reset()

    def to_bytes(self):
        return bytejoin(self) \
               + self.Warnings.to_bytes() \
               + self.Errors.to_bytes() \
               + self.Cells.to_bytes()
