import random

import pika

from brokers import get_connection, CAR_FRAME_QUEUE


def consume_car_frame(channel: pika.adapters.blocking_connection.BlockingChannel, method, props, body):
    randint = random.randint(0, 1)
    if randint == 0:
        print("ack")
        channel.basic_ack(method.delivery_tag)
    else:
        print("nack")
        channel.basic_nack(method.delivery_tag)
    print(bytes.decode(body), props, method)


channel = get_connection()
channel.basic_consume(
    CAR_FRAME_QUEUE,
    consume_car_frame,
    exclusive=True
)
channel.start_consuming()
