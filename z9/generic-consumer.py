#!/usr/bin/env python
import pika
import sys
import time

exchange = sys.argv[1]
queue = sys.argv[2]
routing_key = sys.argv[3] if len(sys.argv) > 3 else None

print("%s --[%s]--> %s" % (exchange, routing_key, queue))
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

def callback(ch, method, properties, body):
    print(" [x] Received %r, %s" % (body, method))
    time.sleep(len(body))
    channel.basic_ack(delivery_tag=method.delivery_tag)
    print("Response ACK %r" % body)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=queue,
                      no_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
