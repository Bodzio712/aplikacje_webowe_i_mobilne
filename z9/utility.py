#!/usr/bin/env python
import pika
import sys
import time
import os
import json

#konfiguracja wstępna kolejki odbieranych danych
exchange = 'pogodzip'
queue = 'pogodzip'
routing_key = 'pogodzip-miniature'

#Do celów debugowania
print("%s --[%s]--> %s" % (exchange, routing_key, queue))

#Podłączanie się do kolejki
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

#Metoda odpowiadająca za odbieranie danych i ich konwesję
def callback(ch, method, properties, body):
    #dekodowanie JSON
    body = body.decode("UTF-8")
    img = json.loads(body)

    #Debugowanie
    print(" [x] Received %r, %s" % (body, method))

    #Konwersja miniatury
    print("convert -resize 64x64! {} {}".format(img['path'] + img['file'], "miniature/" + img['path'] + img['file']))
    os.system("convert -resize 64x64! {} {}".format(img['path'] + img['file'], "miniatures/" + img['path'] + img['file']))

    #Potwierdzenie przetworzenia danych
    channel.basic_ack(delivery_tag=method.delivery_tag)

    #Debugowanie
    print("Response ACK %r" % body)

#Odbieram max jedną pozycję z kolejki
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=queue,
                      no_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
