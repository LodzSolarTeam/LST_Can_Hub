import asyncio
import logging

from utils.backup_handler import BackupHandler
from car import Car

MESSAGES_IN_QUEUE_LIMIT = 10


async def send_scheduler(car: Car, backup_handler: BackupHandler, *args: asyncio.Queue):
    async def queue_message(q: asyncio.Queue, finalMessage):
        try:
            if q.qsize() > MESSAGES_IN_QUEUE_LIMIT:
                logging.warning(
                    f"Too much unprocessed messages, saving {MESSAGES_IN_QUEUE_LIMIT} messages to a file")
                messages = []
                for _ in range(q.qsize()):
                    message = await q.get()
                    q.task_done()
                    messages.append(message)
                backup_handler.backup_messages(messages)

            await q.put(finalMessage)
        except Exception as e:
            logging.warning(f"Error queueing message: " + str(e))

    finalMessage = None
    queues = list(filter(None, args))
    while True:
        if car.canStatus:
            try:
                finalMessage = car.to_bytes()
            except Exception as e:
                logging.warning(f"Failed creating final message: " + str(e))

            for queue in queues:
                await queue_message(queue, finalMessage)

        await asyncio.sleep(0.5)
