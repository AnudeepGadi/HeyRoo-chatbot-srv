#!/usr/bin/env python
import pika
from utils import send_query

connection_url = "amqp://admin:admin1234@localhost:5672"
parameters = pika.URLParameters(connection_url)
parameters.heartbeat = 60
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='rpc_queue')


def on_request(ch, method, props, body):

    body = body.decode("utf-8")
    response = send_query(body)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()