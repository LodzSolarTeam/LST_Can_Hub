from threading import Thread
import time
import logging
import persistqueue

from car import Car

from azure.iot.device import IoTHubDeviceClient, Message
from azure.iot.device.exceptions import ConnectionFailedError

INTERVAL_SEC = 1.0
CONNECTION_STRING = "HostName=lst-mqtt.azure-devices.net;DeviceId=eagletwo;SharedAccessKey=GAX+ltj0Yyl1LpJKSfN9GtOfYLbdd+l/Kdr8CBMjsRU="

queue = persistqueue.SQLiteAckQueue('./car_queue', auto_commit=True, multithreading=True)

def car_send_scheduler(car: Car):
    t = Thread(target=send_to_iot_hub, name="Azure-IoT-Hub")
    t.daemon = True
    t.start()

    def send_car():
        car.fill_timestamp(time.time_ns() // 1_000_000)
        finalMessage = car.to_bytes()
        queue.put(finalMessage)
        car.reset()
        logging.info("Queue put")

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
        time.sleep(((time_init + (INTERVAL_SEC * cptr)) - time_start ))


def send_to_iot_hub():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    while True:
        msg = queue.get()
        logging.info(f"get {msg}")
        try:
            message = Message(msg, message_id="car")
            client.send_message(message)
            queue.ack(msg)    
            logging.info(f"Acked message.")
        except ConnectionFailedError as e:
            queue.nack(msg)
            logging.info(f"Nacked messasge. {e}")