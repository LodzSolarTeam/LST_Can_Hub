import json
import time
import logging
from threading import Thread

import cantools.database.can.signal
import persistqueue

INTERVAL_SEC = 1.0

class NamedSignalValueEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, cantools.database.can.signal.NamedSignalValue):
            return obj.name
        return super().default(obj)

class TransmitterScheduler(Thread):
    def __init__(self, managed_dict: dict, queue: persistqueue.SQLiteAckQueue):
        super().__init__(name="data-send-scheduler")
        self.managed_dict = managed_dict
        self.queue = queue

    def run(self):
        # sleep na sterydach -> https://stackoverflow.com/a/54161792/7598740
        cptr = 0
        time_start = time.time()
        time_init = time.time()
        my_dict = {}
        while True:
            try:
                self.managed_dict["timestamp"] = time.time_ns() // 1_000_000
                finalMessage = json.dumps(self.managed_dict.copy(), cls=NamedSignalValueEncoder)
                self.queue.put(finalMessage)
                logging.info(f"put item in queue")
            except Exception as e:
                logging.warning(f"Failed creating final message: " + self.managed_dict.copy())

            cptr += 0.1
            time_start = time.time()
            time.sleep(((time_init + (INTERVAL_SEC * cptr)) - time_start))
