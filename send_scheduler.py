from datetime import datetime
import struct
import time
import pika
import logging
import broker

from car import Car

INTERVAL_SEC = 5


def send_scheduler(car: Car):
    while True:
        try:
            with broker.get_channel() as channel:
                while True:
                    try:
                        car.fill_timestamp(int(time.time()))
                        finalMessage = car.to_bytes()
                        channel.basic_publish(
                            "amq.direct",
                            "car",
                            finalMessage,
                            pika.BasicProperties(
                                delivery_mode=pika.DeliveryMode.Persistent
                            )
                        )
                        car.init()
                        logging.info("[Send Scheduler] Messsage sent to broker")
                    except Exception as e:
                        logging.warning(f"Failed creating final message: " + str(e))
                    time.sleep(1)
        except:
            logging.warning("Broker connection can't be established")
            time.sleep(0)
