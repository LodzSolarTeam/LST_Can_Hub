#!/usr/bin/env python
import asyncio
from datetime import datetime
import os
import logging
from multiprocessing import Process, Manager

import argparse

import params
from src.communication.can_receiver import can_receiver
from src.communication.mock.can_mock import CanMock
from src.process_transmitter import Transmitter


async def main(config: dict[str, any]):

    manager = Manager()
    managed_params = params.create_managed_params(manager, params.lst_param)

    configure_logging(args_config['file_logging'])
    can_interface = configure_can(args_config['vcan'])

    processes = []
    # processes.append(Process(target=bms_receiver, args=[managed_params], name="BMS-Receiver"))
    # processes.append(Process(target=gps_receiver, args=[managed_params], name="GPS-Receiver"))
    processes.append(Process(target=can_receiver, args=(managed_params, can_interface,), name="can-receiver"))

    if args_config['vcan']:
        processes.append(CanMock())

    # processes.append(Process(target=tpms_receiver, args=[], name="TPMS-Receiver"))
    # processes.append(Process(target=send_timesync, name="Can-Time-Sync"))

    processes.append(Transmitter(managed_params))

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
        logging.info(f"Terminate {repr(manager)}")


def retrieve_args_config():
    parser = argparse.ArgumentParser(description="Eeagle Two Hub",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--vcan", action='store_true', help="Use virtual can interface and send mocked data to it")
    parser.add_argument("--file-logging", action='store_true', help="Logs to file enabled")
    args_config = vars(parser.parse_args())
    return args_config


def configure_logging(is_file_logger_enabled: bool):
    if is_file_logger_enabled:
        print("Logging to terminal and specified file")
        os.system(f"mkdir {DIR}")
        LOG_PATH = f"{DIR}/{dt_now.year}-{dt_now.month}-{dt_now.day} {dt_now.hour}:{dt_now.minute}:{dt_now.second} canhub.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
            handlers=[
                logging.FileHandler(LOG_PATH),
                logging.StreamHandler()
            ])
    else:
        print("Logging to terminal")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
            handlers=[
                logging.StreamHandler()
            ])

def configure_can(use_vcan: bool):
    can_interface = 'vcan0' if use_vcan else 'can0'
    if use_vcan:
        os.system('sudo modprobe vcan')
        os.system('sudo ip link add dev vcan0 type vcan')
        os.system('sudo ip link set up vcan0')
    else:
        os.system('sudo ifconfig can0 down')
        os.system('sudo ip link set can0 type can bitrate 250000')
        os.system('sudo ifconfig can0 up')

    return can_interface

if __name__ == "__main__":
    DIR = "/home/pi/LST_Can_Hub/logs"
    dt_now = datetime.now()
    args_config = retrieve_args_config()

    asyncio.run(
        main(args_config)
    )
