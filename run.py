#!/usr/bin/env python

import asyncio
import glob
import time
import pika
import logging
import ssl
from asyncio.futures import CancelledError
import broker

from car import Car
from receivers.e2_can import can_receiver
from receivers.gps import gps_receiver
from receivers.serial_data_parser import SerialDataParser
from receivers.therm_sensors import motor_temperature_receiver
from send_scheduler import send_scheduler
from utils.backup_handler import BackupHandler, NUMBER_OF_MESSAGES_TO_RESEND
from utils.web_socket import WebSocketConnectWithTimeout, WEBSOCKET_CONNECTION_TIMEOUT

SEND_TO_BOARD_COMPUTER = False  # TODO make it program argument `send-board-computer=[True/False]`
SEND_CLOUD = True  # TODO make it program argument `send-cloud=[True/False]`

LOG_PATH = "logs.log"  # TODO make it program argument `log-path=FILE_NAME`
BACKUP_PATH = "backup.bin"  # TODO make it program argument `backup-path=FILE_NAME`

URI_BOARD_COMPUTER = "ws://192.168.43.117:55201/api/websocket"
URI_STRATEGY = "wss://test-lst-api.azurewebsites.net/api/WebSocket"

car = Car()

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])
    
    logging.info("Waiting for broker connection")
    while True:
        try:
            connection = broker.get_connection()
            broker.init_broker(connection.channel())
            connection.close()
            break
        except Exception as e:
            logging.info("Connection with broker cant be established. Waiting 5 seconds to retry")
            time.sleep(5)

    logging.info("Connection with broker established")

    serial_port = '' if not glob.glob('/dev/ttyUSB*') else glob.glob('/dev/ttyUSB*')[0]
    gps_port = '' if not glob.glob('/dev/gps*') else glob.glob('/dev/gps*')[0]
    can_interface = 'can0'

    logging.info("Starting coroutines")

    loop = asyncio.get_event_loop()

    loop.create_task(SerialDataParser(car, serial_port).start_listening())
    loop.create_task(motor_temperature_receiver(car))
    loop.create_task(gps_receiver(car, gps_port))
    loop.create_task(can_receiver(car, can_interface, mock=True))
    loop.create_task(send_scheduler(car))

    loop.set_debug(False)

    loop.run_forever()


if __name__ == "__main__":
    main()
