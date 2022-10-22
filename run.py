#!/usr/bin/env python

import asyncio
from datetime import datetime
import os
import logging

from multiprocessing import Process
from multiprocessing.managers import BaseManager
import argparse
from car import Car
from receivers.e2_can import can_receiver

from utils.can_faker import can_faker



async def main(config):
    BaseManager.register('Car', Car)
    manager = BaseManager()
    manager.start()
    car = manager.Car()

    USE_VCAN = config['vcan']

    if USE_VCAN:
        os.system('modprobe vcan')
        os.system('ip link add dev vcan0 type vcan')
        os.system('ip link set up vcan0')
    else:
        os.system('ifconfig can0 down')
        os.system('ip link set can0 type can bitrate 250000')
        os.system('ifconfig can0 up')

    CAN_INTERFACE = 'vcan0' if USE_VCAN else 'can0'
    
    processes = []
    # processes.append(Process(target=bms_receiver, args=[car], name="BMS-Receiver"))
    # processes.append(Process(target=gps_receiver, args=[car], name="GPS-Receiver"))

    if USE_VCAN:
        processes.append(Process(target=can_faker, name="CAN-Faker"))
    processes.append(Process(target=can_receiver, args=(car, CAN_INTERFACE, ), name="CAN-Receiver"))

    # processes.append(Process(target=tpms_receiver, args=[car], name="TPMS-Receiver"))

    # processes.append(Process(target=car_send_scheduler, args=(car,), name="Send-Scheduler"))
    # processes.append(Process(target=send_timesync, name="Can-Time-Sync"))   

    for p in processes:
        p.start()
        logging.info(f"Starting {p.name}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Eeagle Two Hub", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--vcan", action='store_true', help="Use virtual can interface and send mocked data to it")
    config = vars(parser.parse_args())

    e = datetime.now()
    dir = "/home/pi/LST_Can_Hub/logs"

    os.system(f"mkdir {dir}")
    LOG_PATH = f"{dir}/{e.year}-{e.month}-{e.day} {e.hour}:{e.minute}:{e.second} canhub.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])

    asyncio.run(
        main(config)
    )
