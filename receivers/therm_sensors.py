import asyncio
import logging
import struct

from w1thermsensor import W1ThermSensor

from car import Car

async def motor_temperature_receiver(car: Car):
    while True:
        try:
            sensors = W1ThermSensor.get_available_sensors()
            logging.info(f"[Motor Temperature Receiver] {sensors}")
            for sensor in sensors:
                temperature = int(
                    float(
                        round(sensor.get_temperature(), 2)
                    ) * 100
                )
                car.General.motorTemperatureArray[:] = struct.pack('<H', temperature)
            await asyncio.sleep(0.7)
        except Exception as e:
            print(str(e))

