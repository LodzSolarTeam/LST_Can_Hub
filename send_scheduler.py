from threading import Thread
import time
import logging
import persistqueue

from car import Car

INTERVAL_SEC = 1.0

queue = persistqueue.SQLiteAckQueue('./car_queue')

def car_send_scheduler(car: Car):
    def send_car():
        car.fill_timestamp(time.time_ns() // 1_000_000)
        finalMessage = car.to_bytes()
        queue.put(finalMessage)
        logging.info("Queue put")
        car.reset()

    # sleep na sterydach -> https://stackoverflow.com/a/54161792/7598740
    cptr = 0
    time_start = time.time()
    time_init = time.time()
    while True:
        try:
            send_car()
        except Exception as e:
            logging.warning(f"Failed creating final message: " + str(e))

        cptr += 1
        time_start = time.time()
        time.sleep(((time_init + (INTERVAL_SEC * cptr)) - time_start))
