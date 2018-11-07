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
@app.route('/pogodzip/login/userfiles/<path:file0>', methods=['GET', 'POST'])
def download(file0):
return send_from_directory(directory='userfiles', filename=file0)
