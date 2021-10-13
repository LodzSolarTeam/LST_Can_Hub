from struct import pack
from datetime import datetime
import logging
from gps import Gps

class Car:
    # GENERAL
    timestamp = bytearray(8)
    throttlePosition = bytearray(1)
    motorController = bytearray(1)
    regenerationBrake = bytearray(1)
    cruiseThrottle = bytearray(1)
    cruiseDesiredSpeed = bytearray(1)
    batteryError = bytearray(1)
    engineError = bytearray(1)
    driveMode = bytearray(1)
    cruiseEngaged = bytearray(1)
    horn = bytearray(1)
    handBrake = bytearray(1)
    temperatures = bytearray(4)
    rpm = bytearray(2)
    solarRadiance = bytearray(2)
    motorTemperature = bytearray(2)
    # BATTERY
    remainingChargeTime = bytearray(4)
    chargerEnabled = bytearray(1)
    systemState = bytearray(1)
    inputOutputState = bytearray(1)
    packCRate = bytearray(2)
    stateOfCharge = bytearray(1)
    stateOfHealth = bytearray(1)
    numberOfCellsConnected = bytearray(1)
    remainingEnergy = bytearray(2)
    deviationOfVoltageInCells = bytearray(2)
    packTemperatureMax = bytearray(1)
    LMUNumberWithMaxTemperature = bytearray(1)
    packTemperatureMin = bytearray(1)
    LMUNumberWithMinTemperature = bytearray(1)
    cellVoltageMax = bytearray(2)
    cellNumberWithMaxVoltage = bytearray(1)
    cellVoltageMin = bytearray(2)
    cellNumberWithMinVoltage = bytearray(1)
    cellAvgVoltage = bytearray(2)
    packVoltage = bytearray(2)
    packCurrent = bytearray(2)
    warnings = bytearray(3)  # BatteryWarnings = 3 bajty
    errors = bytearray(4)  # BatteryErrors = 4 bajty
    # SERIAL DATA
    cells_voltage = bytearray(64)
    cells_temperature = bytearray(16)
    # LIGHTS
    stopLights = bytearray(1)
    lowBeamLights = bytearray(1)
    highBeamLights = bytearray(1)
    rightIndicatorLights = bytearray(1)
    leftIndicatorLights = bytearray(1)
    parkLights = bytearray(1)
    interiorLights = bytearray(1)
    emergencyLights = bytearray(1)
    # SOLAR
    mpptInputVoltage = bytearray(16)  # MpptAmount = 4 uint = 4 bajty
    mpptInputCurrent = bytearray(16)
    mpptOutputVoltage = bytearray(16)
    mpptOutputPower = bytearray(16)
    mpptPcbTemperature = bytearray(8)  # short = 2 bajty
    mpptMofsetTemperature = bytearray(8)
    # TIRES
    pressures = bytearray(4)  # tiresPressureSize = 4
    tiresTemperatures = bytearray(4)  # tiresTemperaturesSize = 4
    # GPS
    gps = Gps()

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
            self.timestamp = self._parse_car_timestamp(timestamp)
        except Exception as err:
            logging.warning(f"Timestamp cannot be converted {timestamp}")
            logging.warning(err)
            logging.warning("Skipping frame")

        # GENERAL
        self.throttlePosition = frames.engines[0:1]
        self.motorController = frames.engines[1:2]
        self._byte_to_bit_array(self.motorController)
        self.regenerationBrake = frames.engines[2:3]
        self.cruiseThrottle = frames.engines[3:4]
        self.cruiseDesiredSpeed = frames.engines[4:5]
        self.batteryError = self._byte_to_bit_array(frames.lights[1:2])[1:2]
        self.engineError = self._byte_to_bit_array(frames.lights[1:2])[2:3]
        driveMode = self._byte_to_bit_array(frames.lights[1:2])
        self.driveMode = (driveMode[4]*2 + driveMode[5]).to_bytes(1, "big")
        self.cruiseEngaged = self._byte_to_bit_array(frames.lights[1:2])[6:7]
        self.horn = self._byte_to_bit_array(frames.lights[0:1])[7:8]
        self.handBrake = self._byte_to_bit_array(frames.lights[1:2])[0:1]
        # car.temperatures # not exisiting
        self.rpm = frames.speed[0:2][::-1]
        self.solarRadiance = frames.sunSensor[0:2]
        # BATTERY
        self.remainingChargeTime = frames.batteryRemainingEnergyFrame[0:2][::-1]
        self.remainingChargeTime.append(frames.batteryRemainingEnergyFrame[2])
        self.remainingChargeTime.append(0x00)
        self.chargerEnabled = frames.batteryMainFrame[6:7]
        self.systemState = frames.batteryMainFrame[4:5]
        self.inputOutputState = frames.batteryOtherDataFrame[4:5]
        self.packCRate = frames.batteryOtherDataFrame[5:7][::-1]
        self.stateOfCharge = frames.batteryMainFrame[5:6]
        self.stateOfHealth = frames.batteryOtherDataFrame[0:1]
        self.numberOfCellsConnected = frames.batteryOtherDataFrame[1:2]
        self.remainingEnergy = frames.batteryRemainingEnergyFrame[3:5][::-1]
        self.deviationOfVoltageInCells = frames.batteryOtherDataFrame[2:4][::-1]
        self.packTemperatureMax = frames.batteryTemperatureFrame[0:1]
        self.LMUNumberWithMaxTemperature = frames.batteryTemperatureFrame[1:2]
        self.packTemperatureMin = frames.batteryTemperatureFrame[2:3]
        self.LMUNumberWithMinTemperature = frames.batteryTemperatureFrame[3:4]
        self.cellVoltageMax = frames.batteryVoltageCellsFrame[6:8][::-1]
        self.cellNumberWithMaxVoltage = frames.batteryVoltageCellsFrame[5:6]
        self.cellVoltageMin = frames.batteryVoltageCellsFrame[3:5][::-1]
        self.cellNumberWithMinVoltage = frames.batteryVoltageCellsFrame[2:3]
        self.cellAvgVoltage = frames.batteryVoltageCellsFrame[0:2][::-1]
        self.packVoltage = frames.batteryMainFrame[0:2][::-1]
        self.packCurrent = frames.batteryMainFrame[2:4][::-1]
        self.warnings = frames.batteryErrorFrame[5:8]
        self.errors = frames.batteryErrorFrame[0:4]
        # LIGHTS
        self.stopLights = self._byte_to_bit_array(frames.lights[0:1])[0:1]
        self.lowBeamLights = self._byte_to_bit_array(frames.lights[0:1])[1:2]
        self.highBeamLights = self._byte_to_bit_array(frames.lights[0:1])[2:3]
        self.rightIndicatorLights = self._byte_to_bit_array(frames.lights[0:1])[3:4]
        self.leftIndicatorLights = self._byte_to_bit_array(frames.lights[0:1])[4:5]
        self.parkLights = self._byte_to_bit_array(frames.lights[0:1])[5:6]
        self.interiorLights = self._byte_to_bit_array(frames.lights[0:1])[5:6]
        self.emergencyLights = self._byte_to_bit_array(frames.lights[0:1])[6:7]
        # SOLAR
        self.mpptInputVoltage = frames.mppt1Input[4:8] + \
            frames.mppt2Input[4:8] + \
            frames.mppt3Input[4:8] + frames.mppt4Input[4:8]
        self.mpptInputCurrent = frames.mppt1Input[0:4] + \
            frames.mppt2Input[0:4] + \
            frames.mppt3Input[0:4] + frames.mppt4Input[0:4]
        self.mpptOutputVoltage = frames.mppt1Output[0:4] + \
            frames.mppt2Output[0:4] + \
            frames.mppt3Output[0:4] + frames.mppt4Output[0:4]
        self.mpptOutputPower = frames.mppt1Output[4:8] + frames.mppt2Output[4:8] + \
            frames.mppt3Output[4:8] + frames.mppt4Output[4:8]
        self.mpptPcbTemperature = frames.mppt1TemperatureData[6:8] + frames.mppt2TemperatureData[6:8] + \
            frames.mppt3TemperatureData[6:8] + frames.mppt4TemperatureData[6:8]
        self.mpptMofsetTemperature = frames.mppt1TemperatureData[4:6] + frames.mppt2TemperatureData[4:6] + \
            frames.mppt3TemperatureData[4:6]+frames.mppt4TemperatureData[4:6]
        # TIRES not exisiting
        # GPS not exisiting
