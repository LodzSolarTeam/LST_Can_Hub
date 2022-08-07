import asyncio
import logging
from datetime import datetime

import pika
import websockets.exceptions
from aio_pika.abc import AbstractIncomingMessage

import broker
from websocket import get_websocket_connection

URL = "ws://0.0.0.0:55201/api/WebSocket"
frames_queue = asyncio.Queue(maxsize=1)


async def consume_car_frame(message: AbstractIncomingMessage) -> None:
    await frames_queue.put(message)
    logging.debug(f"frame_queue.put()")


async def websocket_handler():
    while True:
        try:
            websocket = await get_websocket_connection(URL)
            while True:
                message: AbstractIncomingMessage = await frames_queue.get()
                await websocket.send(message.body)
                await message.ack()
                logging.debug(f"Message acknowledge sent {datetime.utcnow()}")
        except KeyboardInterrupt:
            break
        except Exception:
            logging.warning("Sleep 5 seconds then reconnect")
            await asyncio.sleep(5)
            continue


async def main():
    channel = await broker.get_channel_async()
    queue = await channel.get_queue(broker.CAR_FRAME_QUEUE)

    await queue.consume(consume_car_frame, timeout=10, exclusive=True)
    await websocket_handler()




if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    asyncio.run(main())
