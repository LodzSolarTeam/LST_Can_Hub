import logging
import time

from w1thermsensor import W1ThermSensor

from car import Car

# 4 czujniki, dwa na sterowniku dwa na silnikach 

def motor_temperature_receiver(car: Car):
    logging.info("Initialization")
    while True:
        try:
            sensors = W1ThermSensor.get_available_sensors()
            logging.info(f"{sensors}")
            for sensor in sensors:
                car.fill_motor_temperatures(sensor.id, sensor.get_temperature())
            time.sleep(0.1)
        except Exception as e:
            logging.warning(str(e))


    
        

