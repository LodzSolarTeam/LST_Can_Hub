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

    def save_frame(self, id, data):
        if (id == 321):
            self.engines = data
        elif (id == 770):
            self.lights = data
        elif (id == 1475):
            self.batteryMainFrame = data
        elif (id == 1412):
            self.speed = data
        elif (id == 1029):
            self.sunSensor = data
        elif (id == 1473):
            self.batteryVoltageCellsFrame = data
        elif (id == 1474):
            self.batteryErrorFrame = data
        elif (id == 1476):
            self.batteryTemperatureFrame = data
        elif (id == 1477):
            self.batteryRemainingEnergyFrame = data
        elif (id == 1478):
            self.batteryOtherDataFrame = data
        elif (id == 403105268):
            self.chargerFrame = data
        elif (id == 31260673):
            self.chargeControllerFrame = data
        elif (id == 0):
            self.errorFrame = data
        elif (id == 384):
            self.mppt1Input = data
        elif (id == 640):
            self.mppt1Output = data
        elif (id == 1152):
            self.mppt1TemperatureData = data
        elif (id == 385):
            self.mppt2Input = data
        elif (id == 641):
            self.mppt2Output = data
        elif (id == 1153):
            self.mppt2TemperatureData = data
        elif (id == 386):
            self.mppt3Input = data
        elif (id == 642):
            self.mppt3Output = data
        elif (id == 1154):
            self.mppt3TemperatureData = data
        elif (id == 387):
            self.mppt4Input = data
        elif (id == 643):
            self.mppt4Output = data
        elif (id == 1155):
            self.mppt4TemperatureData = data
