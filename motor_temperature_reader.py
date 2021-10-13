import asyncio
import struct
from w1thermsensor import W1ThermSensor

class MotorTemperatureReader:
    ARRAY_SIZE = 2

    def __init__(self, motorTemperatureArray):
        self.motorTemperatureArray = motorTemperatureArray

    async def start_listening(self):
        while True:
            try:
                for sensor in W1ThermSensor.get_available_sensors():
                    temperature = int(
                        float(
                            round(sensor.get_temperature(), 2)
                        )*100
                    )
                    print(temperature)
                    self.motorTemperatureArray[:] = struct.pack('<H', temperature)
                await asyncio.sleep(0.1)
            except Exception as e:
                print(str(e))

