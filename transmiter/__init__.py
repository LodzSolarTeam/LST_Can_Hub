from multiprocessing import Process
from signal import pthread_kill, SIGTSTP

import persistqueue

from transmiter.car_send_scheduler import CarSendScheduler
from transmiter.mqtt_transmiter import MQTTTransmitter


class EagleTransmitter(Process):
    def __init__(self, car):
        super().__init__(name="Eagle-Transmitter")
        self.car = car
        self.queue = persistqueue.SQLiteAckQueue('./car_queue', multithreading=True)

    def run(self):
        mqtt_transmitter = MQTTTransmitter(self.queue)
        car_send_scheduler = CarSendScheduler(self.car, self.queue)

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
