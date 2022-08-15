import asyncio
import logging
from random import random
import struct
import time
from typing import Mapping

from w1thermsensor import W1ThermSensor

from car import Car

# 4 czujniki, dwa na sterowniku dwa na silnikach 



async def motor_temperature_receiver(car: Car):
    def map(id, value):
        if id == "1":
            car.General.lMotorTemperature = struct.pack("f", value)
        elif id == "2":
            car.General.rMotorTemperature = struct.pack("f", value)
        elif id == "3":
            car.General.lControllerTemperature = struct.pack("f", value)
        elif id == "4":
            car.General.rControllerTemperature = struct.pack("f", value)
    loop = asyncio.get_event_loop()
    while True:
        try:
            sensors = W1ThermSensor.get_available_sensors()
            logging.debug(f"[Motor Temperature Receiver] {sensors}")
            for sensor in sensors:
                logging.error(repr(sensor))
                map(id, sensor.get_temperature())
            await loop.run_in_executor(None, time.sleep, 1)
        except Exception as e:
            logging.warning(str(e))

