'''
Loading config from .env/.env.<env_name> file.
By default .env is used.
Specific file name should be passed as first command line parameter.
'''
import os
import sys

from dotenv import load_dotenv, find_dotenv

env_file = find_dotenv(sys.argv[1] if len(sys.argv) > 1 else '.env')

if not load_dotenv(dotenv_path=env_file, override=True):
    raise EnvironmentError(f'Cannot load environment from file "{env_file}"')


class Config:
    def __init__(self):
        self.MONGODB_HOST = os.environ.get('MONGODB_HOST')
        self.MONGODB_PORT = os.environ.get('MONGODB_PORT')
        self.MONGODB_USER = os.environ.get('MONGODB_USER')
        self.MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
        self.MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME')
        self.RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
        self.RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
        self.RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
        self.RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
        self.RABBITMQ_VIRTUAL_HOST = os.environ.get('RABBITMQ_VIRTUAL_HOST')
        self.RABBITMQ_QUEUE_NAME = os.environ.get('RABBITMQ_QUEUE_NAME')
        self.RABBITMQ_QUEUE_NAME_RESULT = os.environ.get('RABBITMQ_QUEUE_NAME_RESULT')

    @property
    def rabbitmq_url(self):
        return f'amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VIRTUAL_HOST}'

    @property
    def mongodb_url(self):
        return f'mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/'


config = Config()
