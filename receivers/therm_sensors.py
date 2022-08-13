import asyncio
import logging
import time
import struct

from w1thermsensor import W1ThermSensor

from car import Car

async def motor_temperature_receiver(car: Car):
    loop = asyncio.get_event_loop()
    while True:
        try:
            sensors = W1ThermSensor.get_available_sensors()
            logging.debug(f"[Motor Temperature Receiver] {sensors}")
            for sensor in sensors:
                temperature = int(
                    float(
                        round(sensor.get_temperature(), 2)
                    ) * 100
                )
                
            # car.General.motorTemperatureArray[:] = struct.pack('<H', temperature)
            await loop.run_in_executor(None, time.sleep, 1)
        except Exception as e:
            logging.warning(str(e))

