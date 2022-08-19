import asyncio
from datetime import datetime
import logging

from aio_pika.abc import AbstractIncomingMessage

import broker
from utils.web_socket import get_websocket_connection

# URI_STRATEGY = "ws://10.11.11.50:55201/api/WebSocket"
URI_STRATEGY = "wss://test-lst-api.azurewebsites.net/api/WebSocket"
# URI_STRATEGY = "wss://lst-api-v1.azurewebsites.net/api/WebSocket"

e = datetime.now()

async def consume_car_frame(message: AbstractIncomingMessage, frames_queue) -> None:
    await frames_queue.put(message)
    logging.info(f"frame_queue.put()")
        

async def websocket_handler(frames_queue: asyncio.Queue):
    message = None
    while True:
        try:
            logging.info(f"Connecting to websocket")
            websocket = await get_websocket_connection(URI_STRATEGY)
            logging.info(f"Websocket connection established")
            while True:
                message: AbstractIncomingMessage = await frames_queue.get()
                await websocket.send(message.body)
                await message.ack()
                logging.info(f"ACK")
        except KeyboardInterrupt:
            if message is not None:
                await message.nack()
                logging.warning(f"NACK")
            break
        except Exception as e:
            if message is not None:
                await message.nack()
                logging.warning(f"NACK")
            await asyncio.sleep(1)
            continue


async def main():
    frames_queue = asyncio.Queue(maxsize=1)
    channel = await ( await broker.get_connection_async()).channel()
    logging.info("channel connection established")
    queue = await channel.get_queue(broker.CAR_FRAME_QUEUE)
    logging.info("queue established")

    async def consume_car_frame_wrapper(message: AbstractIncomingMessage):
        await consume_car_frame(message, frames_queue)
    await queue.consume(
        consume_car_frame_wrapper,
        timeout=3,
        exclusive=True,
    )
    logging.info("broker consumer initalized")
    await websocket_handler(frames_queue)
    logging.info("websocket handler initalized")




def cloud_sender():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]) 
    print("SSIJ MI CHUJA")
    logging.info("suuck my kurwa dick")
    asyncio.run(main())
