import asyncio
import struct

from w1thermsensor import W1ThermSensor

from car import Car

@asyncio.coroutine
async def motor_temperature_receiver(car: Car):
    while True:
        try:
            for sensor in W1ThermSensor.get_available_sensors():
                temperature = int(
                    float(
                        round(sensor.get_temperature(), 2)
                    ) * 100
                )
                # print(temperature)
                car.General.motorTemperatureArray[:] = struct.pack('<H', temperature)
            await asyncio.sleep(0)
        except Exception as e:
            print(str(e))

