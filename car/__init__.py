import logging
from datetime import datetime
from struct import pack

from car.battery import Battery
from car.general import General
from car.gps import Gps
from car.lights import Lights
from car.solar import Solar
from car.tires import Tires


class Car:
    canStatus = False
    General = General()
    Battery = Battery()
    Lights = Lights()
    Solar = Solar()
    Tires = Tires()
    Gps = Gps()

    def to_bytes(self):
        return self.General.to_bytes() \
               + self.Battery.to_bytes() \
               + self.Lights.to_bytes() \
               + self.Solar.to_bytes() \
               + self.Tires.to_bytes() \
               + self.Gps.to_bytes()

    def _parse_car_timestamp(self, timestamp):
        # for tests: 1559297416.090523
        date = datetime.fromtimestamp(timestamp)
        int_timestamp = round((date - datetime(1970, 1, 1)).total_seconds())
        return pack("Q", int_timestamp)

    def _byte_to_bit_array(self, byte):
        bit_string = ''.join(format(ord(byte), '08b'))
        bits = list(map(int, bit_string))
        return bytearray(bits[::-1])

    def fill_car_model(self, timestamp, frames):
        try:
            self.General.timestamp = self._parse_car_timestamp(timestamp)
        except Exception as err:
            logging.warning(f"Timestamp cannot be converted {timestamp}")
            logging.warning(err)
            logging.warning("Skipping frame")

        # GENERAL
        self.General.throttlePosition = frames.engines[0:1]
        self.General.motorController = frames.engines[1:2]
        self._byte_to_bit_array(self.General.motorController)
        self.General.regenerationBrake = frames.engines[2:3]
        self.General.cruiseThrottle = frames.engines[3:4]
        self.General.cruiseDesiredSpeed = frames.engines[4:5]
        self.General.batteryError = self._byte_to_bit_array(frames.lights[1:2])[1:2]
        self.General.engineError = self._byte_to_bit_array(frames.lights[1:2])[2:3]
        driveMode = self._byte_to_bit_array(frames.lights[1:2])
        self.General.driveMode = (driveMode[4] * 2 + driveMode[5]).to_bytes(1, "big")
        self.General.cruiseEngaged = self._byte_to_bit_array(frames.lights[1:2])[6:7]
        self.General.horn = self._byte_to_bit_array(frames.lights[0:1])[7:8]
        self.General.handBrake = self._byte_to_bit_array(frames.lights[1:2])[0:1]
        # car.temperatures # not exisiting
        self.General.rpm = frames.speed[0:2][::-1]
        self.General.solarRadiance = frames.sunSensor[0:2]
        # BATTERY
        self.Battery.remainingChargeTime = frames.batteryRemainingEnergyFrame[0:2][::-1]
        self.Battery.remainingChargeTime.append(frames.batteryRemainingEnergyFrame[2])
        self.Battery.remainingChargeTime.append(0x00)
        self.Battery.chargerEnabled = frames.batteryMainFrame[6:7]
        self.Battery.systemState = frames.batteryMainFrame[4:5]
        self.Battery.inputOutputState = frames.batteryOtherDataFrame[4:5]
        self.Battery.packCRate = frames.batteryOtherDataFrame[5:7][::-1]
        self.Battery.stateOfCharge = frames.batteryMainFrame[5:6]
        self.Battery.stateOfHealth = frames.batteryOtherDataFrame[0:1]
        self.Battery.numberOfCellsConnected = frames.batteryOtherDataFrame[1:2]
        self.Battery.remainingEnergy = frames.batteryRemainingEnergyFrame[3:5][::-1]
        self.Battery.deviationOfVoltageInCells = frames.batteryOtherDataFrame[2:4][::-1]
        self.Battery.packTemperatureMax = frames.batteryTemperatureFrame[0:1]
        self.Battery.LMUNumberWithMaxTemperature = frames.batteryTemperatureFrame[1:2]
        self.Battery.packTemperatureMin = frames.batteryTemperatureFrame[2:3]
        self.Battery.LMUNumberWithMinTemperature = frames.batteryTemperatureFrame[3:4]
        self.Battery.cellVoltageMax = frames.batteryVoltageCellsFrame[6:8][::-1]
        self.Battery.cellNumberWithMaxVoltage = frames.batteryVoltageCellsFrame[5:6]
        self.Battery.cellVoltageMin = frames.batteryVoltageCellsFrame[3:5][::-1]
        self.Battery.cellNumberWithMinVoltage = frames.batteryVoltageCellsFrame[2:3]
        self.Battery.cellAvgVoltage = frames.batteryVoltageCellsFrame[0:2][::-1]
        self.Battery.packVoltage = frames.batteryMainFrame[0:2][::-1]
        self.Battery.packCurrent = frames.batteryMainFrame[2:4][::-1]
        self.Battery.Warnings.warnings = frames.batteryErrorFrame[5:8]
        self.Battery.Errors.errors = frames.batteryErrorFrame[0:4]
        # LIGHTS
        self.Lights.stopLights = self._byte_to_bit_array(frames.lights[0:1])[0:1]
        self.Lights.lowBeamLights = self._byte_to_bit_array(frames.lights[0:1])[1:2]
        self.Lights.highBeamLights = self._byte_to_bit_array(frames.lights[0:1])[2:3]
        self.Lights.rightIndicatorLights = self._byte_to_bit_array(frames.lights[0:1])[3:4]
        self.Lights.leftIndicatorLights = self._byte_to_bit_array(frames.lights[0:1])[4:5]
        self.Lights.parkLights = self._byte_to_bit_array(frames.lights[0:1])[5:6]
        self.Lights.interiorLights = self._byte_to_bit_array(frames.lights[0:1])[5:6]
        self.Lights.emergencyLights = self._byte_to_bit_array(frames.lights[0:1])[6:7]
        # SOLAR
        self.Solar.mpptInputVoltage = frames.mppt1Input[4:8] + \
                                      frames.mppt2Input[4:8] + \
                                      frames.mppt3Input[4:8] + frames.mppt4Input[4:8]
        self.Solar.mpptInputCurrent = frames.mppt1Input[0:4] + \
                                      frames.mppt2Input[0:4] + \
                                      frames.mppt3Input[0:4] + frames.mppt4Input[0:4]
        self.Solar.mpptOutputVoltage = frames.mppt1Output[0:4] + \
                                       frames.mppt2Output[0:4] + \
                                       frames.mppt3Output[0:4] + frames.mppt4Output[0:4]
        self.Solar.mpptOutputPower = frames.mppt1Output[4:8] + frames.mppt2Output[4:8] + \
                                     frames.mppt3Output[4:8] + frames.mppt4Output[4:8]
        self.Solar.mpptPcbTemperature = frames.mppt1TemperatureData[6:8] + frames.mppt2TemperatureData[6:8] + \
                                        frames.mppt3TemperatureData[6:8] + frames.mppt4TemperatureData[6:8]
        self.Solar.mpptMofsetTemperature = frames.mppt1TemperatureData[4:6] + frames.mppt2TemperatureData[4:6] + \
                                           frames.mppt3TemperatureData[4:6] + frames.mppt4TemperatureData[4:6]
        # TIRES not exisiting
        # GPS not exisiting
