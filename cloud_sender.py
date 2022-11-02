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

        self.current_message = None

        logging.info("Initialized")

    def run(self):
        self.mqtt_client.connect(host, keepalive=True)
        self.mqtt_client.loop_start()

        while True:
            try:
                self.current_message = self.queue.get()
                logging.info(f"get {self.current_message}")

                info = self.mqtt_client.publish("eagle2", self.current_message)
                info.wait_for_publish()

                self.queue.ack(self.current_message)
            except Exception as e:
                logging.error(f"Error: {e}")
                self.queue.nack(self.current_message)

            self.current_message = None

        self.mqtt_client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code " + str(rc))

async def main():
    cloud_sender = CloudSender()
    cloud_sender.run()

def cloud_sender():
    asyncio.run(main())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cloud_sender()
