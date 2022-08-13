#!/usr/bin/env python

import asyncio
from datetime import datetime, tzinfo
import os
import time
import logging
import broker

from car import Car
from receivers.e2_can import can_receiver
from receivers.gps import gps_receiver
from receivers.serial_data_parser import bms_receiver
from receivers.therm_sensors import motor_temperature_receiver
from send_scheduler import send_scheduler

e = datetime.now()
LOG_PATH = f"./logs/{e.year}-{e.month}-{e.day} {e.hour}:{e.minute}:{e.second} canhub_producer_logs.log"

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])
    logging.info("==================================== Waiting for broker")
    while True:
        try:
            connection = broker.get_connection()
            broker.init_broker(connection.channel())
            connection.close()
            break
        except Exception as e:
            logging.info("Connection with broker cant be established. Waiting 1 seconds to retry")
            time.sleep(1)


    car = Car()
    loop = asyncio.get_event_loop()

    loop.create_task(motor_temperature_receiver(car))
    loop.create_task(bms_receiver(car)())
    loop.create_task(gps_receiver(car))
    loop.create_task(can_receiver(car, mock=False))
    loop.create_task(send_scheduler(car))

    loop.set_debug(False)

    loop.run_forever()


if __name__ == "__main__":
    os.system("python3 consume_to_cloud.py &")
    main()
