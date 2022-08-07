import logging

import pika

BROKER_USER = 'toor'
BROKER_PASS = 'toor'

CAR_FRAME_QUEUE = "car_frame_queue"


async def get_channel_async():
    import aio_pika
    connection = await aio_pika.connect(login=BROKER_USER, password=BROKER_PASS)
    return await connection.channel()

# Channel per thread
def get_channel():
    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASS)
    connection_param = pika.connection.ConnectionParameters(credentials=credentials)
    connection = pika.BlockingConnection(connection_param)
    return connection.channel()


with get_channel() as channel:
    channel.queue_declare(
        queue=CAR_FRAME_QUEUE,
        durable=True,
        arguments={
            "x-overflow": "drop-head",  # drop "oldest" message
            "x-max-length": 10 * 60,  # messages from 10 minutes (if message per second)
            "x-queue-mode": "lazy",  # Set the queue into lazy mode, keeping as many messages as possible on disk
        }
    )
    channel.queue_bind(
        queue=CAR_FRAME_QUEUE,
        exchange="amq.direct",  # this exchange exists by default
        routing_key="car"
    )
