import time
import logging
from threading import Thread

from car import Car

INTERVAL_SEC = 1.0


class CarSendScheduler(Thread):
    def __init__(self, car: Car, queue):
        super().__init__(name="Car-Send-Scheduler", daemon=True)
        self.car = car
        self.queue = queue

    def run(self):
        # sleep na sterydach -> https://stackoverflow.com/a/54161792/7598740
        cptr = 0
        time_start = time.time()
        time_init = time.time()
        while True:
            try:
                self.car.fill_timestamp(time.time_ns() // 1_000_000)
                finalMessage = self.car.to_bytes()
                self.queue.put(finalMessage)
                self.queue.task_done()
                logging.info("Queue put")
                self.car.reset()
            except Exception as e:
                logging.warning(f"Failed creating final message: " + str(e))

            cptr += 1
            time_start = time.time()
            time.sleep(((time_init + (INTERVAL_SEC * cptr)) - time_start))
