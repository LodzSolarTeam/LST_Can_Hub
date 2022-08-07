import pika

BROKER_USER = 'toor'
BROKER_PASS = 'toor'

CAR_FRAME_QUEUE = "car_frame_queue"


# Channel per thread
def get_connection():
    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASS)
    connection_param = pika.connection.ConnectionParameters(credentials=credentials)
    connection = pika.BlockingConnection(connection_param)
    return connection.channel()


with get_connection() as channel:
    res = channel.queue_declare(
        queue=CAR_FRAME_QUEUE,
        durable=True,
        arguments={
            "x-overflow": "drop-head",  # drop "oldest" message
            "x-max-length": 10 * 60,  # messages from 10 minutes (if message per second)
            "x-queue-mode": "lazy",  # Set the queue into lazy mode, keeping as many messages as possible on disk
        }
    )
    print(f"declare_queue queue={CAR_FRAME_QUEUE}", res)
    res = channel.queue_bind(
        queue=CAR_FRAME_QUEUE,
        exchange="amq.direct",  # this exchange exists by default
        routing_key="car"
    )
    print(f"queue_bind queue={CAR_FRAME_QUEUE} exchange=amq.direct routing_key=car", res)
