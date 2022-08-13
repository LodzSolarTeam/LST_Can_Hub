from datetime import datetime
import struct
import time
import pika
import asyncio
import logging
import broker

from car import Car

INTERVAL_SEC = 1


async def send_scheduler(car: Car):
    def _parse_time(timestamp):
        date = datetime.utcfromtimestamp(timestamp)
        int_timestamp = round((date - datetime(1970, 1, 1)).total_seconds())
        return struct.pack("Q", int_timestamp)

    start_time = time.time()
    loop = asyncio.get_event_loop()
    while True:
        try:
            with broker.get_channel() as channel:
                while True:
                    if car.canStatus and (time.time() - start_time > INTERVAL_SEC):
                        start_time = time.time()
                        try:
                            car.General.timestamp = _parse_time(time.time())
                            finalMessage = car.to_bytes()
                            channel.basic_publish(
                                "amq.direct",
                                "car",
                                finalMessage,
                                pika.BasicProperties(
                                    delivery_mode=pika.DeliveryMode.Persistent
                                )
                            )
                            logging.debug("[Send Scheduler] Messsage sent to broker")
                        except Exception as e:
                            logging.warning(f"Failed creating final message: " + str(e))

                    await loop.run_in_executor(None, time.sleep, 0)
        except:
            logging.warning("Broker connection can't be established")
            await loop.run_in_executor(None, time.sleep, 0)
