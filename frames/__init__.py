import logging

class Frames:
    # CORE CAN:
    engines = bytearray(5)
    lights = bytearray(2)
    batteryMainFrame = bytearray(8)
    speed = bytearray(8)
    sunSensor = bytearray(8)

    # BATERY
    errorFrame = bytearray(8)
    batteryVoltageCellsFrame = bytearray(8)
    batteryErrorFrame = bytearray(8)
    batteryTemperatureFrame = bytearray(4)
    batteryRemainingEnergyFrame = bytearray(5)
    batteryOtherDataFrame = bytearray(8)
    chargerFrame = bytearray(5)
    chargeControllerFrame = bytearray(5)

    # MPPT
    mppt1Input = bytearray(8)
    mppt1Output = bytearray(8)
    mppt1TemperatureData = bytearray(8)
    mppt2Input = bytearray(8)
    mppt2Output = bytearray(8)
    mppt2TemperatureData = bytearray(8)
    mppt3Input = bytearray(8)
    mppt3Output = bytearray(8)
    mppt3TemperatureData = bytearray(8)
    mppt4Input = bytearray(8)
    mppt4Output = bytearray(8)
    mppt4TemperatureData = bytearray(8)

    canStatus = 0b0000_0000_0000_0000_0000_0000_0000_0000 # 4 bytes

    def save_frame(self, id, data):
        self.canStatus = 0b0
        if (id == 321):
            self.canStatus |= 0b1
            self.engines = data
        elif (id == 770):
            self.canStatus |= 0b1 << 1
            self.lights = data
        elif (id == 1475):
            self.canStatus |= 0b1 << 2
            self.batteryMainFrame = data
        elif (id == 1412):
            self.canStatus |= 0b1 << 3
            self.speed = data
        elif (id == 1413):
            logging.info(f"temp {data}") # TODO TEMPERATURES 
        elif (id == 1029):
            self.canStatus |= 0b1 << 4
            self.sunSensor = data
        elif (id == 1473):
            self.canStatus |= 0b1 << 5
            self.batteryVoltageCellsFrame = data
        elif (id == 1474):
            self.canStatus |= 0b1 << 6
            self.batteryErrorFrame = data
        elif (id == 1476):
            self.canStatus |= 0b1 << 7
            self.batteryTemperatureFrame = data
        elif (id == 1477):
            self.canStatus |= 0b1 << 8
            self.batteryRemainingEnergyFrame = data
        elif (id == 1478):
            self.canStatus |= 0b1 << 9
            self.batteryOtherDataFrame = data
        elif (id == 403105268):
            self.canStatus |= 0b1 << 10
            self.chargerFrame = data
        elif (id == 31260673):
            self.canStatus |= 0b1 << 11
            self.chargeControllerFrame = data
        elif (id == 0):
            self.canStatus |= 0b1 << 12
            self.errorFrame = data
        elif (id == 384):
            self.canStatus |= 0b1 << 13
            self.mppt1Input = data
        elif (id == 640):
            self.canStatus |= 0b1 << 14
            self.mppt1Output = data
        elif (id == 1152):
            self.canStatus |= 0b1 << 15
            self.mppt1TemperatureData = data
        elif (id == 385):
            self.canStatus |= 0b1 << 16
            self.mppt2Input = data
        elif (id == 641):
            self.canStatus |= 0b1 << 17
            self.mppt2Output = data
        elif (id == 1153):
            self.canStatus |= 0b1 << 18
            self.mppt2TemperatureData = data
        elif (id == 386):
            self.canStatus |= 0b1 << 19
            self.mppt3Input = data
        elif (id == 642):
            self.canStatus |= 0b1 << 20
            self.mppt3Output = data
        elif (id == 1154):
            self.canStatus |= 0b1 << 21
            self.mppt3TemperatureData = data
        elif (id == 387):
            self.canStatus |= 0b1 << 22
            self.mppt4Input = data
        elif (id == 643):
            self.canStatus |= 0b1 << 23
            self.mppt4Output = data
        elif (id == 1155):
            self.canStatus |= 0b1 << 24
            self.mppt4TemperatureData = data
