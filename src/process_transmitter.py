from multiprocessing import Process
from signal import pthread_kill, SIGTSTP

import persistqueue

from src.frames import EagleTwoProxy
from src.schedule_thread_transmitter import TransmitterScheduler
from src.mqtt_thread_transmitter import TransmitterMqtt


class Transmitter(Process):
    def __init__(self, frameProxy: EagleTwoProxy):
        super().__init__(name="Transmitter")
        self.frameProxy = frameProxy
        self.queue = persistqueue.SQLiteAckQueue('./car_queue', multithreading=True)

    def run(self):
        mqtt_transmitter = TransmitterMqtt(self.queue)
        car_send_scheduler = TransmitterScheduler(self.frameProxy, self.queue)

        while True:
            mqtt_transmitter.start()
            car_send_scheduler.start()
            try:
                mqtt_transmitter.join()
                car_send_scheduler.join()
            except KeyboardInterrupt:
                break
            pthread_kill(mqtt_transmitter.ident, SIGTSTP)
            pthread_kill(car_send_scheduler.ident, SIGTSTP)
