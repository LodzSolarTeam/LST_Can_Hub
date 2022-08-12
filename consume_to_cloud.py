from ast import arg
import asyncio
import logging
from datetime import datetime

from aio_pika.abc import AbstractIncomingMessage

import broker
from utils.web_socket import get_websocket_connection

URL = "wss://test-lst-api.azurewebsites.net/api/WebSocket"

    

async def consume_car_frame(message: AbstractIncomingMessage, frames_queue) -> None:
    await frames_queue.put(message)
    logging.debug(f"frame_queue.put()")


async def websocket_handler(frames_queue):
    message = None
    while True:
        try:
            websocket = await get_websocket_connection(URL)
            while True:
                message: AbstractIncomingMessage = await frames_queue.get()
                await websocket.send(message.body)
                await message.ack()
                logging.debug(f"Message acknowledge sent {datetime.utcnow()}")
        except KeyboardInterrupt:
            if message is not None:
                await message.nack()
            break
        except Exception as e:
            if message is not None:
                await message.nack()
            logging.warning(f"Sleep 5 seconds then reconnect. {e}")
            await asyncio.sleep(5)
            continue


async def main():
    frames_queue = asyncio.Queue(maxsize=1)
    channel = await broker.get_channel_async()
    queue = await channel.get_queue(broker.CAR_FRAME_QUEUE)

    async def consume_car_frame_wrapper(message: AbstractIncomingMessage):
        await consume_car_frame(message, frames_queue)

    await queue.consume(
        consume_car_frame_wrapper,
        timeout=3,
        exclusive=True,
    )
    await websocket_handler(frames_queue)




if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    asyncio.run(main())
