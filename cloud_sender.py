import asyncio
import logging
import time
import persistqueue
from azure.iot.device import IoTHubDeviceClient, Message
from azure.iot.device.exceptions import ConnectionFailedError

CONNECTION_STRING = "HostName=lst-mqtt.azure-devices.net;DeviceId=eagletwo;SharedAccessKey=GAX+ltj0Yyl1LpJKSfN9GtOfYLbdd+l/Kdr8CBMjsRU="

async def main():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    queue = persistqueue.SQLiteAckQueue('./car_queue', auto_commit=True)
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

def cloud_sender():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())