#!/usr/bin/env python

import asyncio
from datetime import datetime
import os
import logging

from multiprocessing.managers import BaseManager
import argparse

from car import Car
from transmiter import EagleTransmitter

from utils.can_faker import CanFaker


async def main(config: dict[str, any]):
    use_vcan = config['vcan']
    can_interface = 'vcan0' if use_vcan else 'can0'

    BaseManager.register('car', Car)
    car_manager = BaseManager()
    car_manager.start()
    car = car_manager.car()

    if use_vcan:
        os.system('sudo modprobe vcan')
        os.system('sudo ip link add dev vcan0 type vcan')
        os.system('sudo ip link set up vcan0')
    else:
        os.system('sudo ifconfig can0 down')
        os.system('sudo ip link set can0 type can bitrate 250000')
        os.system('sudo ifconfig can0 up')

    processes = []
    # processes.append(Process(target=bms_receiver, args=[car], name="BMS-Receiver"))
    # processes.append(Process(target=gps_receiver, args=[car], name="GPS-Receiver"))

    if use_vcan:
        processes.append(CanFaker())

    # processes.append(Process(target=tpms_receiver, args=[car], name="TPMS-Receiver"))
    # processes.append(Process(target=send_timesync, name="Can-Time-Sync"))

    processes.append(EagleTransmitter(car))


    for p in processes:
        p.start()
        logging.info(f"Starting {p.name}")
    try:
        for p in processes:
            p.join()
        car_manager.join()
    except KeyboardInterrupt:
        for p in processes:
            logging.info(f"Terminate {p.name}")
            p.kill()
        logging.info(f"Terminate {repr(car_manager)}")


if __name__ == "__main__":
    DIR = "/home/pi/LST_Can_Hub/logs"

    parser = argparse.ArgumentParser(description="Eeagle Two Hub",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--vcan", action='store_true', help="Use virtual can interface and send mocked data to it")
    args_config = vars(parser.parse_args())

    e = datetime.now()

    os.system(f"mkdir {DIR}")
    LOG_PATH = f"{DIR}/{e.year}-{e.month}-{e.day} {e.hour}:{e.minute}:{e.second} canhub.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])

    asyncio.run(
        main(args_config)
    )
