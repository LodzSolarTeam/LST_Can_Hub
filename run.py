#!/usr/bin/env python

import asyncio
from datetime import datetime
import os
import logging
import broker

from multiprocessing import Process
from multiprocessing.managers import BaseManager
from can_time_sync import send_timesync


from car import Car
from cloud_sender import cloud_sender
from receivers.e2_can import can_receiver
from receivers.gps import gps_receiver
from receivers.serial_data_parser import bms_receiver
from send_scheduler import send_scheduler

e = datetime.now()
LOG_PATH = f"./logs/{e.year}-{e.month}-{e.day} {e.hour}:{e.minute}:{e.second} canhub.log"

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ]) 
    logging.info("Waiting for broker")
    c = await broker.get_connection_async()
    await c.close()
    logging.info("Broker OK")

    BaseManager.register('Car', Car)
    manager = BaseManager()
    manager.start()
    car = manager.Car()

    MOCK = False
    processes = []
    processes.append(Process(target=bms_receiver, args=[car], name="BMS-Receiver"))
    processes.append(Process(target=gps_receiver, args=[car], name="GPS-Receiver"))
    processes.append(Process(target=can_receiver, args=[car, MOCK], name="CAN-Receiver"))

    processes.append(Process(target=send_scheduler, args=[car], name="Send-Scheduler"))
    processes.append(Process(target=cloud_sender, name="Cloud-Sender"))
    processes.append(Process(target=send_timesync, name="Can-Time-Sync"))
    

    for p in processes:
        p.start()
        logging.info(f"Starting {p.name}")

    try:
        for p in processes:
            p.join()
        manager.join()
    except KeyboardInterrupt:
        for p in processes:
            logging.info(f"Terminate {p.name}")
            p.kill()
        logging.info(f"Terminate {manager.name}")
        manager.kill()


if __name__ == "__main__":
    os.system("mkdir ./logs")
    asyncio.run(
        main()
    )
