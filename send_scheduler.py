import time
import pika
import asyncio
import logging
import broker

from car import Car

INTERVAL_SEC = 1

async def send_scheduler(car: Car):
    start_time = time.time()
    while True:
        try:
            with broker.get_channel() as channel:
                while True:
                    if car.__canStatus and (time.time() - start_time > INTERVAL_SEC):
                        start_time = time.time()
                        try:
                            finalMessage = car.to_bytes()
                            channel.basic_publish(
                                "amq.direct",
                                "car",
                                finalMessage,
                                pika.BasicProperties(
                                    delivery_mode=pika.DeliveryMode.Persistent
                                )
                            )
                            logging.info("[Send Scheduler] Messsage sent to broker")
                        except Exception as e:
                            logging.warning(f"Failed creating final message: " + str(e))

                    await asyncio.sleep(0)
        except:
            logging.warning("Broker connection can't be established")
            await asyncio.sleep(0)
