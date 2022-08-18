#!/usr/bin/env python

import asyncio
from datetime import datetime
import os
import time
import logging
import broker

from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager


from car import Car
from receivers.e2_can import can_receiver
from receivers.gps import gps_receiver
from receivers.serial_data_parser import bms_receiver
from receivers.therm_sensors import motor_temperature_receiver
from send_scheduler import send_scheduler

e = datetime.now()
LOG_PATH = f"./logs/{e.year}-{e.month}-{e.day} {e.hour}:{e.minute}:{e.second} canhub_producer_logs.log"

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
        ])
    logging.info("==================================== Waiting for broker")
    while True:
        try:
            await (await broker.get_connection_async()).close()
            break
        except Exception as e:
            logging.info("Connection with broker cant be established. Waiting 1 seconds to retry")
            time.sleep(1)
        
    BaseManager.register('Car', Car)
    manager = BaseManager()
    manager.start()
    car = manager.Car()

    MOCK = True
    processes = []

    processes.append(Process(target=motor_temperature_receiver, args=[car], name="MT"))
    processes.append(Process(target=bms_receiver, args=[car], name="BMS"))
    processes.append(Process(target=gps_receiver, args=[car], name="GPS"))
    processes.append(Process(target=can_receiver, args=[car, MOCK], name="CAN"))
    processes.append(Process(target=send_scheduler, args=[car], name="SendScheduler"))

    os.system("python3 ./run-cloud-sender.py")

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
        manager.join()
    except KeyboardInterrupt:
        for p in processes:
            p.kill()
        manager.kill()


if __name__ == "__main__":
    os.system("mkdir ./logs")
    asyncio.run(
        main()
    )
