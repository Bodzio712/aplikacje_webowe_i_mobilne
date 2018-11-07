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
@app.route('/pogodzip/transfer/userfiles/<path:file0>', methods=['GET', 'POST'])
def download(file0):
    token = request.form['token']
    if tokenVerified(token):
        return send_from_directory(directory='userfiles', filename=file0)
    else:
        return redirect('/pogodzip/login/logout')

#Trasownik do metody obsługującej wysyłanie piku
@app.route('/pogodzip/transfer/uploading', methods=['POST'])
def uploading():
    token = request.form['token']
    print(token)
    if tokenVerified(token):
        user = getUserFromToken(token)
        path = 'userfiles/' + str(user) + '/'
        files = os.listdir('userfiles/' + str(user) + '/')
        toUpload = request.files['file']
        if len(files) <5:
            toUpload.save(path + toUpload.filename)
            return redirect('/pogodzip/login/home')
        else:
            return redirect('/pogodzip/login/home')
    else:
      return redirect('/pogodzip/login/login')

def tokenVerified(token):
    token_parts = {}
    print(token)
    try:
        token_parts = jwt.decode(token, jwt_secret_key)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        return False
    return token_parts['login'] == str(r.hget('pogodzip:webapp:' + token_parts['sid'], 'login'))[2:-1]

def getUserFromToken(token):
    token_parts = {}
    try:
        token_parts = jwt.decode(token, jwt_secret_key)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        return False
    return token_parts['login']
