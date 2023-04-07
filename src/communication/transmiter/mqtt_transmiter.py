import logging
import time
from threading import Thread

import paho.mqtt.client as mqtt
import persistqueue

DEVICE_ID = "ec69637a-89cb-4976-9a73-2979adf3e484"
host = "192.168.1.27"


class MQTTTransmitter(Thread):
    is_running: bool
    is_connection_established: bool
    queue: persistqueue.SQLiteAckQueue
    current_message: dict

    def __init__(self, queue: persistqueue.SQLiteAckQueue):
        super().__init__(name="MQTT-Transmitter")
        self.is_running = True
        self.is_connection_established = False
        self.queue = queue
        self.current_message = {}
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_connection_established
        self.client.on_connect_fail = self.mqtt_connection_dropped
        self.client.on_disconnect = self.mqtt_disconnect

    def run(self):
        try:
            self.client.connect(host)
        except ConnectionRefusedError as e:
            logging.error(e)
        finally:
            self.client.loop_start()
        while self.is_running:
            while self.is_connection_established and self.is_running:
                self.publisher_runner()
            else:
                logging.warning("MQTT Connection not established")
                time.sleep(1)

    def publisher_runner(self):
        try:
            self.current_message = self.queue.get()
            if not self.client.is_connected():
                logging.info("not_connected")
                self.queue.nack(self.current_message)
            self.client.publish(
                f'{DEVICE_ID}/data/send-data',
                self.current_message,
                qos=1
            )
            self.client.loop_write()
            self.queue.ack(self.current_message)
            self.queue.clear_acked_data(keep_latest=0)
            self.queue.task_done()
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.is_running = False
        except Exception as e:
            logging.error(f"Error: {e}")
            self.queue.nack(self.current_message)
        self.current_message = {}

    def mqtt_connection_established(self, client: mqtt.Client, userdata, flags, reasonCode):
        """
            The value of rc indicates success or not:
                0: Connection successful
                1: Connection refused - incorrect protocol version
                2: Connection refused - invalid client identifier
                3: Connection refused - server unavailable
                4: Connection refused - bad username or password
                5: Connection refused - not authorised
        """
        logging.error(f"mqtt_connection_established reason code = {reasonCode}")
        if reasonCode == 0:
            self.is_connection_established = True

    def mqtt_connection_dropped(self, client: mqtt.Client, userdata):
        logging.error("mqtt_connection_dropped")
        self.is_connection_established = False

    def mqtt_disconnect(self, client: mqtt.Client, userdata, reasonCode):
        logging.error("mqtt_disconnect")
        self.is_connection_established = False

    def mqtt_socket_close(self, client: mqtt.Client, userdata, socket):
        logging.error("mqtt_socket_close")
        self.is_connection_established = False
