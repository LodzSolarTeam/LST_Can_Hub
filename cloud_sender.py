import asyncio
import logging
import threading
import time
from persistqueue import SQLiteAckQueue
from paho.mqtt.client import Client
from paho.mqtt.publish import single

host = "127.0.0.1"
# host = "<URL TO REMOTE MQTT BROKER>"

class CloudSender:
    def __init__(self):
        self.queue = SQLiteAckQueue('./car_queue')
        self.mqtt_client = Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_publish = self.on_publish

        self.current_message = None

        logging.info("inited")

    def run(self):
        # self._run_queue()
        self.mqtt_client.connect(host, keepalive=True)
        self.mqtt_client.loop_start()

        while True:
            logging.info("Waiting for message")
            self.current_message = self.queue.get()
            logging.info(f"get {self.current_message}")

            # qos=1 means that the broker will make sure that the message is delivered
            info = self.mqtt_client.publish("eagle2", self.current_message)
            info.wait_for_publish()

        self.mqtt_client.loop_stop()


    def on_connect(self, client, userdata, flags, rc):

        logging.info("Connected with result code " + str(rc))


    def on_publish(self, client, userdata, mid):
        logging.info(f"Published `{self.current_message}` with mid `{mid}` and userdata `{userdata}`")

        if userdata == None:
            logging.info("Message published")
            self.queue.ack(self.current_message)
        else:
            logging.info("Message not published")
            self.queue.nack(self.current_message)

async def main():
    cloud_sender = CloudSender()
    cloud_sender.run()

def cloud_sender():
    asyncio.run(main())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cloud_sender()
