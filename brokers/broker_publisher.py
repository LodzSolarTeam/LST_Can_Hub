import time
import pika

from brokers import get_connection

with get_connection() as channel:
    for i in range(1):
        channel.basic_publish(
            "amq.direct",
            "car",
            "{car_frame}".encode(encoding="UTF8"),
            pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            )
        )
        print("sent")
        time.sleep(5)
