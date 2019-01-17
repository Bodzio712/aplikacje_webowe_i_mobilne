# coding: utf-8

from flask import Flask
from flask import session
from flask import request
from flask import render_template
from flask import redirect
from flask import send_from_directory
from flask import url_for

import csv
import os
import uuid
import redis
import jwt
import datetime
import json
import pika

app = Flask(__name__)

app.secret_key = b'35325fsdgsdg4gsd3fsge'

#Wczytywanie kluczy z pliku sec.cfg
with open ('sec.cfg', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        if row['key'] == 'client_secret':
            auth_client_secret = row['value']
        if row['key'] == 'jwt_secret_key':
            jwt_secret_key = row['value']


r = redis.Redis()

#Trasownik do pobierania plików
@app.route('/pogodzip/dl/userfiles/<path:file0>', methods=['GET', 'POST'])
def download(file0):
    token = request.form['token']
    if checkToken(token):
        return send_from_directory(directory='userfiles', filename=file0)
    else:
        return redirect('/pogodzip/webapp/logout')

#Trasownik do metody obsługującej wysyłanie piku
@app.route('/pogodzip/dl/uploading', methods=['POST'])
def uploading():
        user = request.form["token"]
        path = str(user) + '/'
        files = os.listdir( str(user) + '/')
        toUpload = request.files['file']
        if len(files) <5:
            toUpload.save(path + toUpload.filename)
            if (toUpload.filename.endswith('.jpg')):
                sendToQueue(path)
            return redirect('/pogodzip/webapp/home')
        else:
            return redirect('/pogodzip/webapp/home')

#Wyciąganie danych z tokena
def checkToken(token):
    token_parts = {}
    #Odkomentuj poniższą odpcję do debudowania (sprawdzanie czy token jest przesyłany)
    #print(token)
    try:
        token_parts = jwt.decode(token, jwt_secret_key)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        #False jesli wystąpi wyjątek (brak tokena lub token wygasł)
        return False
    return token_parts['login'] == str(r.hget('pogodzip:webapp:' + token_parts['sid'], 'login'))[2:-1]

#Wyciąganie nazwy użytkownika
def getUser(token):
    token_parts = {}
    try:
        token_parts = jwt.decode(token, jwt_secret_key)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        return False
    return token_parts['login']

#Wysyłanie pliku do kolejki
def sendToQueue(path):
    #Wybór trybu itd.
    exchange = 'pogodzip'
    exchange_type = 'direct'
    routing_key = 'pogodzip-miniature'

    #Formatowanie danych do JSON
    toUpload = request.files['file']
    data = json.dumps({'path': path, 'file': toUpload.filename})

    #Definiowanie zawartości w body
    body = '{}'.format(data)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange,
                         exchange_type=exchange_type)
    channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=body)
    connection.close()

