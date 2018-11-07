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
import jwt
import datetime
import redis

app = Flask(__name__)
app.secret_key = b'35325fsdgsdg4gsd3fsge'
jwt_secret_key = '124hgjhghj214214124jj'

r = redis.Redis()

#Trasownik do strony głównej
@app.route('/pogodzip/login/')
@app.route('/pogodzip/login/index')
@app.route('/pogodzip/login/index.html')
def index():
    return render_template('index.html')

#Trasownik do logowania
@app.route('/pogodzip/login/login')
@app.route('/pogodzip/login/login.html')
def login():
    return render_template('login.html')

#Trasownik do okna rejestracji
@app.route('/pogodzip/login/register')
@app.route('/pogodzip/login/register.html')
def register():
    return render_template('register.html')

#Trasownik do panelu użytkownika
@app.route('/pogodzip/login/home')
@app.route('/pogodzip/login/home.html')
@app.route('/pogodzip/login/download')
def home():
    if session.get('user'):
        user = session['user']
        token = session['token']
        path = '/pogodzip/transfer/userfiles/' + str(user) + '/'
        files = os.listdir('userfiles/' + str(user) + '/')

        #Przypisywanie ściezek do pilków
        if len(files) >= 1:
            file0 = files[0]
            path0 = path + file0
        else:
            file0 = ''
            path0 = ''
        if len(files) >= 2:
            file1 = files[1]
            path1 = path + file1
        else:
            file1 = ''
            path1 = ''
        if len(files) >= 3:
            file2 = files[2]
            path2 = path + file2
        else:
            file2 = ''
            path2 = ''
        if len(files) >= 4:
            file3 = files[3]
            path3 = path + file3
        else:
            file3 = ''
            path3 = ''
        if len(files) >= 5:
            file4 = files[4]
            path4 = path + file4
        else:
            file4 = ''
            path4 = ''

        return render_template('home.html', user=user, file0=file0, file1=file1, file2=file2, file3=file3, file4=file4, path0=path0, path1=path1, path2=path2, path3=path3, path4=path4, token=token)
    else:
        return redirect('/pogodzip/login/login')

#Trasownik do wylogowywania się
@app.route('/pogodzip/login/logout')
def logout():
    r.delete('pogodzip:webapp:' + session['sid'])
    session.pop('user', None)
    session.pop('sid', None)
    session.pop('token', None)
    return redirect('/pogodzip/login/')

#Trasownik do sprawdzania rejestracji
@app.route('/pogodzip/login/checkRegister', methods=['POST'])
def checkRegister():
    _login = request.form['login']
    _password = request.form['pass']

    with open('users', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        #Sprawdzanie wprowadzonych danych z zdefioniowanymi w pliku CSV
        for row in reader:
            if _login == row['login']:
                return redirect('/pogodzip/login/')

    f = open("users", "a")
    f.write(_login + "," + _password +"\n")
    f.close()
    path = "userfiles/"+_login
    os.makedirs(path)
    return redirect('/pogodzip/login/login')


#Trasownik do sprawdzania logowania
@app.route('/pogodzip/login/checkLogin', methods=['POST'])
def checkLogin():
    _login = request.form['login']
    _password = request.form['pass']

    if checkUser(_login, _password):
        session['user'] = _login
        sid = str(uuid.uuid4())
        token_elems = {
            'login': _login,
            'sid': sid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }
        token = str(jwt.encode(token_elems, jwt_secret_key))[2:-1]
        r.hset('pogodzip:webapp:'+sid, 'login', _login)
        session['sid'] = sid
        session['token'] = token
        return redirect('/pogodzip/login/home')
    return redirect('/pogodzip/login/login')

#Trasownik do pliku .CSS
@app.route('/pogodzip/login/static/style.css', methods=['GET'])
def downloadCss():
    return send_from_directory(directory='static', filename='style.css')

#Trasownik do wysyłania plików
@app.route('/pogodzip/login/upload')
@app.route('/pogodzip/login/upload.html')
def upload():
    return render_template('upload.html', token=session['token'])

#Sprawdzanie użytkowników
def checkUser(login, password):
    redisPass = str(r.hget('pogodzip:webapp:users', login))[2:-1]
    if redisPass == password:
        return True
    return False
