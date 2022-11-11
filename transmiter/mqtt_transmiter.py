import logging
from threading import Thread

from paho.mqtt.client import Client

host = "123.123.123.123"
# host = "<URL TO REMOTE MQTT BROKER>"

class MQTTTransmitter(Thread):
    def __init__(self, queue):
        super().__init__(name="MQTT-Transmitter")
        self.queue = queue
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
                logging.info("wait_for_publish")
                info.wait_for_publish()
                logging.info("published")

                self.queue.ack(self.current_message)
            except KeyboardInterrupt:
                self.mqtt_client.loop_stop()
                break
            except Exception as e:
                logging.error(f"Error: {e}")
                self.queue.nack(self.current_message)
            self.current_message = None

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code " + str(rc))
