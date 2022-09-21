#!/usr/bin/env python

import asyncio
from datetime import datetime
import os
import logging

from multiprocessing import Process
from multiprocessing.managers import BaseManager

from car import Car
from receivers.e2_can import can_receiver


async def main():
    BaseManager.register('Car', Car)
    manager = BaseManager()
    manager.start()
    car = manager.Car()

    processes = []
    # processes.append(Process(target=bms_receiver, args=[car], name="BMS-Receiver"))
    # processes.append(Process(target=gps_receiver, args=[car], name="GPS-Receiver"))
    processes.append(Process(target=can_receiver, args=(car, True, ), name="CAN-Receiver"))
    # processes.append(Process(target=tpms_receiver, args=[car], name="TPMS-Receiver"))

    # processes.append(Process(target=car_send_scheduler, args=(car,), name="Send-Scheduler"))
    # processes.append(Process(target=send_timesync, name="Can-Time-Sync"))   

    for p in processes:
        p.start()
        logging.info(f"Starting {p.name}")


if __name__ == "__main__":
    e = datetime.now()
    LOG_PATH = f"/home/pi/LST_Can_Hub/logs/{e.year}-{e.month}-{e.day} {e.hour}:{e.minute}:{e.second} canhub.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])

    os.system("mkdir /home/pi/LST_Can_Hub/logs")
    os.system('ifconfig can0 down')
    os.system('ip link set can0 type can bitrate 250000')
    os.system('ifconfig can0 up')

    asyncio.run(
        main()
    )
