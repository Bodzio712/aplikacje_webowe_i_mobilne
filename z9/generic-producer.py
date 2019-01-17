#!/usr/bin/env python
import pika
import sys
from uuid import uuid4
from random import randint

exchange = sys.argv[1]
exchange_type = sys.argv[2]
routing_key = sys.argv[3] if len(sys.argv) > 3 else ''

print("==> %s ==> %s (%s)" % (routing_key, exchange, exchange_type))

body = ''
number = randint(1, 9)
i = 0
while i < number:
    body += '.'
    i += 1

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange,
                         exchange_type=exchange_type)
channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=body)
print(" [x] Sent '{}'".format(body))
connection.close()
