import asyncio
import logging
import pika
import aio_pika

BROKER_USER = 'toor'
BROKER_PASS = 'toor'

CAR_FRAME_QUEUE = "car_frame_queue"


async def get_connection_async():
    while True:
        try:
            connection: aio_pika.abc.AbstractConnection = await aio_pika.connect(login=BROKER_USER, password=BROKER_PASS)
            channel = await connection.channel()
            await init_broker(channel)
            return connection 
        except Exception as e:
            logging.info("Cant establish connection with broker. Retry in 1 seconds")
            await asyncio.sleep(1)

def get_connection():
    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASS)
    connection_param = pika.connection.ConnectionParameters(credentials=credentials)
    connection = pika.BlockingConnection(connection_param)
    return connection

# Channel per thread
def get_channel():
    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASS)
    connection_param = pika.connection.ConnectionParameters(credentials=credentials)
    connection = pika.BlockingConnection(connection_param)
    return connection.channel()


async def init_broker(channel: aio_pika.abc.AbstractChannel):
    queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
        name=CAR_FRAME_QUEUE,
        durable=True,
        arguments={
            "x-overflow": "drop-head",  # drop "oldest" message
            "x-max-length": 60 * 60 * 6,  # messages from 10 minutes (if message per second)
            "x-queue-mode": "lazy",  # Set the queue into lazy mode, keeping as many messages as possible on disk
        }
    )

    await queue.bind(
        exchange="amq.direct",  # this exchange exists by default
        routing_key="car"
    )
