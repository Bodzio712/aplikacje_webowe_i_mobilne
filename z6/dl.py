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

app = Flask(__name__)

app.secret_key = b'35325fsdgsdg4gsd3fsge'
jwt_secret_key =  '124hgjhghj214214124jj'

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
    if checkToken(request.form['token']):
        user = getUser(token)
        path = 'userfiles/' + str(user) + '/'
        files = os.listdir('userfiles/' + str(user) + '/')
        toUpload = request.files['file']
        if len(files) <5:
            toUpload.save(path + toUpload.filename)
            return redirect('/pogodzip/webapp/home')
        else:
            return redirect('/pogodzip/webapp/home')
    
    return redirect('/pogodzip/webapp/login')

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
