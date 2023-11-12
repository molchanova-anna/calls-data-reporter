'''
Script generates messages for the queue, predefined in .env* under RABBITMQ_QUEUE_NAME
'''
import json
import string
import random

from broker import BrokerConnectionContextManager
from config import config


MESSAGE_COUNT = 100

def fill_queue():
    with BrokerConnectionContextManager() as conn:
        conn.channel.queue_declare(queue=config.RABBITMQ_QUEUE_NAME,
                                   durable=True)
        for i in range(MESSAGE_COUNT):
            message = {
                    "correlation_id": ''.join(random.choice(string.digits) for i in range(14)),
                    "phones": [random.randint(0, 100) for _ in range(10)]
            }
            conn.channel.basic_publish(
                    exchange='',
                    routing_key=config.RABBITMQ_QUEUE_NAME,
                    body=json.dumps(message).encode(),
                )


if __name__ == '__main__':
    fill_queue()
