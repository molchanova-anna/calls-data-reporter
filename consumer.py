'''
Calls data reporter application.
Gets messages from RabbitMQ queue, process data and put results to another RabbitMQ queue.
'''
import datetime
import json
import pika

import db
from broker import BrokerConnection
from config import config

conn_consumer = None
conn_publisher_results = None


def do_calls_data_report_callback(ch, method, properties, body):
    start_time = datetime.datetime.now()
    result = {}
    try:
        body = json.loads(body.decode())
        # db query
        data = db.get_stat_for_calls_list(body.get('phones', []))
        result['data'] = data
        status = 'Complete'
    except Exception as e:
        status = f'Error: {str(e)}'
    correlation_id = body.get('correlation_id')
    result['correlation_id'] = correlation_id
    result['status'] = status
    result['task_received'] = start_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    result['from'] = 'report_service'
    result['to'] = 'client'
    task_total_time = datetime.datetime.now() - start_time
    result['total_duration'] = task_total_time.total_seconds()
    # proceed our message to new step
    process_message(result)
    # acknowledge queue the message has been proceeded successfully
    channel.basic_ack(delivery_tag=method.delivery_tag)


# Sending report
def process_message(data: dict):
    global conn_publisher_results

    if not conn_publisher_results:
        conn_publisher_results = BrokerConnection()
        conn_publisher_results.connect()

    conn_publisher_results.channel.basic_publish(
            exchange='',
            routing_key=config.RABBITMQ_QUEUE_NAME_RESULT,
            body=json.dumps(data).encode(),
        )


if __name__ == "__main__":
    try:
        conn_consumer = pika.BlockingConnection(pika.URLParameters(url=config.rabbitmq_url))
    except Exception as e:
        raise(e)
    channel = conn_consumer.channel()
    channel.queue_declare(queue=config.RABBITMQ_QUEUE_NAME,
                                  durable=True)
    channel.queue_declare(queue=config.RABBITMQ_QUEUE_NAME_RESULT,
                                  durable=True)
    channel.basic_qos(prefetch_count=5)
    channel.basic_consume(queue=config.RABBITMQ_QUEUE_NAME,
                          on_message_callback=do_calls_data_report_callback)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
