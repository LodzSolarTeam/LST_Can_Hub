import asyncio
import logging
import persistqueue

async def main():
    queue = persistqueue.SQLiteAckQueue('./car_queue')

    while True:
        msg = queue.get()
        logging.info(f"get {msg}")
        try:
            # TODO: send to cloud

            queue.ack(msg)
            logging.info(f"Acked message.")
        except Exception as e:
            queue.nack(msg)
            logging.info(f"Nacked messasge. {e}")

def cloud_sender():
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
