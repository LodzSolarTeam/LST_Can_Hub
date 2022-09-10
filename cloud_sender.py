import asyncio
import datetime
import logging

from aio_pika.abc import AbstractIncomingMessage

import broker
import struct 
from utils.web_socket import get_websocket_connection

# URI_STRATEGY = "ws://192.168.8.114:55201/api/WebSocket"
# URI_STRATEGY = "ws://10.11.11.50:55201/api/WebSocket"
# URI_STRATEGY = "ws://172.20.10.3:55201/api/WebSocket"
URI_STRATEGY = "wss://test-lst-api.azurewebsites.net/api/WebSocket" 
# URI_STRATEGY = "wss://lst-api-v1.azurewebsites.net/api/WebSocket" 

async def consume_car_frame(message: AbstractIncomingMessage, frames_queue) -> None:
    await frames_queue.put(message)
    logging.info(f"frame_queue.put")
        

async def websocket_handler(frames_queue: asyncio.Queue):
    message = None
    while True:
        try:
            logging.info(f"Connecting to websocket")
            websocket = await get_websocket_connection(URI_STRATEGY)
            logging.info(f"Websocket connection established")
            while True:
                if message is None:
                    logging.info(f"before frames_queue.get")
                    message: AbstractIncomingMessage = await frames_queue.get()
                    logging.info(f"after frames_queue.get")
                #######################
                target_datetime_ms = struct.unpack("Q", message.body[0:8])[0]
                base_datetime = datetime.datetime(1970, 1, 1)
                delta = datetime.timedelta(0, 0, 0, target_datetime_ms)
                target_datetime = base_datetime + delta
                #######################
                logging.info(f"Sending")
                await websocket.send(message.body)
                await message.ack()
                message = None
                logging.info(f"ACK {target_datetime}")
        except KeyboardInterrupt:
            logging.info("END")
            break
        except Exception as e:
            if message is not None:
                logging.info(f"NACK {target_datetime}")
                message.nack()
            logging.debug(f"Exception occured: {str(e)}")
            await asyncio.sleep(1)


async def main():
    frames_queue = asyncio.Queue(maxsize=1)
    channel = await ( await broker.get_connection_async()).channel()
    await channel.set_qos(prefetch_count=1)
    logging.info("channel connection established")
    queue = await channel.get_queue(broker.CAR_FRAME_QUEUE)
    logging.info("queue established")

    async def consume_car_frame_wrapper(message: AbstractIncomingMessage):
        await consume_car_frame(message, frames_queue)
    await queue.consume(
        consume_car_frame_wrapper,
        exclusive=True,
    )
    logging.info("broker consumer initalized")
    await websocket_handler(frames_queue)
    logging.info("websocket handler initalized")




def cloud_sender():
    asyncio.run(main())
