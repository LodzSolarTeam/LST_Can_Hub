#!/usr/bin/env python

import asyncio
import glob
import logging
import ssl
from asyncio.futures import CancelledError

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
URI_STRATEGY = "wss://lst-api-v1.azurewebsites.net/api/WebSocket"

car = Car()
backup_handler = BackupHandler(BACKUP_PATH, len(car.to_bytes()))


async def send_frame_message(q: asyncio.Queue, url):
    logging.debug(f"Start messages coroutine for {url}")
    message = b""
    messages_to_resend = []
    ssl_context = ssl.create_default_context()
    while True:
        try:
            if url[0:3] == "wss":
                async with WebSocketConnectWithTimeout(url, ssl=ssl_context,
                                                       connect_timeout=WEBSOCKET_CONNECTION_TIMEOUT) as websocket:
                    while True:
                        message = await q.get()
                        q.task_done()
                        await websocket.send(message)
                        logging.info("WebSocket message sent")

                        messages_to_resend = backup_handler.get_unsent_messages(NUMBER_OF_MESSAGES_TO_RESEND)
                        for msg in messages_to_resend:
                            await websocket.send(msg)
                            messages_to_resend.remove(msg)
                            logging.debug("WebSocket Backup message sent")
            else:
                async with WebSocketConnectWithTimeout(url, connect_timeout=WEBSOCKET_CONNECTION_TIMEOUT) as websocket:
                    while True:
                        message = await q.get()
                        q.task_done()
                        await websocket.send(message)
                        message = b""

        except CancelledError:
            raise
        except Exception as e:
            logging.warning(f"Failed sending msg to " + url + ": " +
                            str(type(e).__name__) + ". Saving message to the backup file.")
            if message:
                backup_handler.backup_messages([message])
            if messages_to_resend:
                backup_handler.backup_messages(messages_to_resend)
            await asyncio.sleep(0.1)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])

    queue_board_computer = asyncio.Queue() if SEND_TO_BOARD_COMPUTER else None
    queue_cloud = asyncio.Queue() if SEND_CLOUD else None

    serial_port = glob.glob('/dev/ttyUSB*')[0]
    gps_port = glob.glob('/dev/gps*')[0]
    can_interface = 'can0'

    logging.info("Starting coroutines")
    tasks = [
        asyncio.Task(send_frame_message(queue_board_computer, URI_BOARD_COMPUTER)) if SEND_TO_BOARD_COMPUTER else None,
        asyncio.Task(send_frame_message(queue_cloud, URI_STRATEGY)) if SEND_CLOUD else None,
        asyncio.Task(SerialDataParser(car, serial_port).start_listening()),
        asyncio.Task(motor_temperature_receiver(car)),
        asyncio.Task(gps_receiver(car, gps_port)),
        asyncio.Task(can_receiver(car, can_interface)),
        asyncio.Task(send_scheduler(car, backup_handler, queue_cloud, queue_board_computer))
    ]
    await asyncio.wait(
        list(filter(None, tasks)),
        return_when=asyncio.ALL_COMPLETED
    )


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
