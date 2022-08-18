import asyncio
import logging
from random import random
import struct
import time
from typing import Mapping

from w1thermsensor import W1ThermSensor

from car import Car

# 4 czujniki, dwa na sterowniku dwa na silnikach 



def motor_temperature_receiver(car: Car):
    while True:
        try:
            sensors = W1ThermSensor.get_available_sensors()
            logging.info(f"{sensors}")
            for sensor in sensors:
                car.fill_motor_temperatures(sensor.id, sensor.get_temperature())
            time.sleep(0.5)
        except Exception as e:
            logging.warning(str(e))


    
        

