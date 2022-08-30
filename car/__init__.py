import datetime
import logging
import struct
from car.battery import Battery
from car.general import General
from car.gps import Gps
from car.lights import Lights
from car.solar import Solar
from car.tires import Tires
import pynmea2

class Car:

    General = General()
    Battery = Battery()
    Lights = Lights()
    Solar = Solar()
    Tires = Tires()
    Gps = Gps()

    def __init__(self):
        self.init()

    def init(self):
        self.General = General()
        self.Battery = Battery()
        self.Lights = Lights()
        self.Solar = Solar()
        self.Tires = Tires()
        self.Gps = Gps()
        mock_datetime = datetime.datetime(2005, 4, 2, 21, 37)
        self.Gps.dateYear = struct.pack("H", mock_datetime.year)
        self.Gps.dateMonth = struct.pack("B", mock_datetime.month)
        self.Gps.dateDay = struct.pack("B", mock_datetime.day)
        self.Gps.timeHour = struct.pack("B", mock_datetime.hour)
        self.Gps.timeMin = struct.pack("B", mock_datetime.minute)
        self.Gps.timeSec = struct.pack("B", mock_datetime.second)

    def to_bytes(self):
        return self.General.to_bytes() \
               + self.Battery.to_bytes() \
               + self.Lights.to_bytes() \
               + self.Solar.to_bytes() \
               + self.Tires.to_bytes() \
               + self.Gps.to_bytes()


    def _byte_to_bit_array(self, byte):
        bit_string = ''.join(format(ord(byte), '08b'))
        bits = list(map(int, bit_string))
        return bytearray(bits[::-1])

    def fill_motor_temperatures(self, sensor_id, value):
        logging.debug(f"motor temperatures gathered {sensor_id}")
        if sensor_id == "01193a797781":
            self.General.lControllerTemperature = struct.pack("f", value)
        elif sensor_id == "01193a51b1d5":
            self.General.rControllerTemperature = struct.pack("f", value)
        elif sensor_id == "3":
            self.General.lMotorTemperature = struct.pack("f", value)
        elif sensor_id == "4":
            self.General.rMotorTemperature = struct.pack("f", value)

    def fill_timestamp(self, timestamp):
        self.General.timestamp = struct.pack("Q", timestamp)

    def fill_bms_data(self, cells_temperature, cells_voltage):
        logging.debug("BMS gathered")
        self.Battery.Cells.temperatures = cells_temperature
        self.Battery.Cells.voltages = cells_voltage

    def fill_gps_data(self, msg: pynmea2.TalkerSentence):
        if msg.sentence_type == 'GGA':
            data: pynmea2.GGA = msg
            if msg.is_valid:
                msg
                self.Gps.latitude = struct.pack('d', data.latitude)
                self.Gps.latitudeDirection = struct.pack('B', ord(data.lat_dir))
                self.Gps.longitude = struct.pack('d', msg.longitude)
                self.Gps.longitudeDirection = struct.pack('B', ord(data.lon_dir))
                self.Gps.altitude = struct.pack('d', data.altitude)
                self.Gps.satellitesNumber = struct.pack('B', int(data.num_sats))
                self.Gps.quality = struct.pack('b', data.gps_qual)
                logging.debug("GGA gathered")
            else:
                logging.warning("GGA is not valid")
        if msg.sentence_type == 'RMC':
            data: pynmea2.RMC = msg
            if msg.is_valid:
                self.Gps.latitude = struct.pack('d', data.latitude)
                self.Gps.latitudeDirection = struct.pack('B', ord(data.lat_dir))
                self.Gps.longitude = struct.pack('d', data.longitude)
                self.Gps.longitudeDirection = struct.pack('B', ord(data.lon_dir))
                self.Gps.speedKilometers = struct.pack('d', data.spd_over_grnd)
                logging.debug("RMC gathered")
            else:
                logging.warning("RMC is not valid")

    def fill_can_data(self, frames):
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
        self.General.rpm = frames.speed[0:2][::-1]
        self.General.solarRadiance = frames.sunSensor[0:2]
        self.General.canStatus = struct.pack("I", frames.canStatus)
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
