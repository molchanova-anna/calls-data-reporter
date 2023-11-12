import pika

from config import config

class BrokerConnection():
    connection = None
    channel = None

    def connect(self):
        if not self.connection:
            self.connection = pika.BlockingConnection(pika.URLParameters(url=config.rabbitmq_url))
            self.channel = self.connection.channel()

    def disconnect(self):
        self.channel.close()
        self.connection.close()


class BrokerConnectionContextManager(BrokerConnection):
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()