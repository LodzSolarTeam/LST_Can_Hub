from datetime import datetime
import struct
import time
import pika
import logging
import broker

from car import Car

INTERVAL_SEC = 1.0


def send_scheduler(car: Car):
    while True:
        try:
            with broker.get_channel() as channel:
                # sleep na sterydach -> https://stackoverflow.com/a/54161792/7598740
                cptr = 0
                time_start = time.time()
                time_init = time.time()
                while True:
                    try:
                        car.fill_timestamp(time.time_ns() // 1_000_000)
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
                    cptr += 1
                    time_start = time.time()
                    time.sleep(((time_init + (INTERVAL_SEC * cptr)) - time_start ))
        except:
            logging.warning("Broker connection can't be established")
            time.sleep(0)
