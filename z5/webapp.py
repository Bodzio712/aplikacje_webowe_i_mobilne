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

#Wstępna konfiguracja aplikacji
app = Flask(__name__)
app.secret_key = b'35325fsdgsdg4gsd3fsge'
jwt_secret_key = '124hgjhghj214214124jj'

#Inicjalizacja bazy danych Redis
r = redis.Redis()

#Trasownik do strony głównej
@app.route('/pogodzip/webapp/')
@app.route('/pogodzip/webapp/index')
@app.route('/pogodzip/webapp/index.html')
def index():
    return render_template('index.html')

#Trasownik do logowania
@app.route('/pogodzip/webapp/login')
@app.route('/pogodzip/webapp/login.html')
def login():
    return render_template('login.html')

#Trasownik do okna rejestracji
@app.route('/pogodzip/webapp/register')
@app.route('/pogodzip/webapp/register.html')
def register():
    return render_template('register.html')

#Trasownik do panelu użytkownika/pobierania
@app.route('/pogodzip/webapp/home')
@app.route('/pogodzip/webapp/home.html')
@app.route('/pogodzip/webapp/download')
def home():
    if session.get('user'):
        #Wyciąganie danych o użytkowniku
        user = session['user']
        token = session['token']
        userfiles = str(r.hget('pogodzip:webapp:paths', user))[2:-1]
        path = '/pogodzip/dl/' + userfiles + '/'
        files = os.listdir(userfiles)

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
        #Renderowanie strony z plikami do pobrania
        return render_template('home.html', user=user, file0=file0, file1=file1, file2=file2, file3=file3, file4=file4, path0=path0, path1=path1, path2=path2, path3=path3, path4=path4, token=token)
    else:
        #Przekierowanie do logowania jeśli uzytkownik nie jest zalogowany
        return redirect('/pogodzip/webapp/login')

#Trasownik do wylogowywania się
@app.route('/pogodzip/webapp/logout')
def logout():
    #Usuwanie danych o sesji z bazy danych
    r.delete('pogodzip:webapp:' + session['sid'])
    #Wygaszanie ciasteczka
    session.pop('user', None)
    session.pop('sid', None)
    session.pop('token', None)
    #Przekierowanie do strony głównej aplikacji
    return redirect('/pogodzip/webapp/')

#Trasownik do rejezstrowania użytkownika
@app.route('/pogodzip/webapp/checkRegister', methods=['POST'])
def checkRegister():
    _login = request.form['login']
    _password = request.form['pass']

    if r.hget('pogodzip:webapp:users', _login) == None:
        #Generowanie SIDa do uniezależneinia nazwy katalogu użytkownika od nazwy użytkownika
        sid = str(uuid.uuid4())
        #Dodawanie użytkownika do bazy danych
        r.hset('pogodzip:webapp:users', _login, _password)
        #Generowanie katalogu użytkownika na podstawie SIDa
        path = "userfiles/"+sid
        os.makedirs(path)
        #Dodawanie ścieżki do bazy danych, która przechowuje dane o powiązaniach nazwy użytkownika z katalogiem
        r.hset('pogodzip:webapp:paths', _login, path)
    return redirect('/pogodzip/webapp/login')


#Trasownik do sprawdzania logowania
@app.route('/pogodzip/webapp/checkLogin', methods=['POST'])
def checkLogin():
    _login = request.form['login']
    _password = request.form['pass']

    if checkUser(_login, _password):
        session['user'] = _login
        sid = str(uuid.uuid4())
        #Wpisywanie danych do tokena JWT
        token_elems = {
            'login': _login,
            'sid': sid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }
        #Generowanie tokena
        token = str(jwt.encode(token_elems, jwt_secret_key))[2:-1]
        #Dodawanie sesji użytkownika do bazy Redis
        r.hset('pogodzip:webapp:'+sid, 'login', _login)
        session['sid'] = sid
        session['token'] = token
        return redirect('/pogodzip/webapp/home')
    return redirect('/pogodzip/webapp/login')

#Trasownik do pliku .CSS
@app.route('/pogodzip/webapp/static/style.css', methods=['GET'])
def downloadCss():
    return send_from_directory(directory='static', filename='style.css')

#Trasownik do strony wysyłania plików
@app.route('/pogodzip/webapp/upload')
@app.route('/pogodzip/webapp/upload.html')
def upload():
    return render_template('upload.html', token=session['token'])

#Sprawdzanie poprawności danych logowania
def checkUser(login, _password):
    password = str(r.hget('pogodzip:webapp:users', login))[2:-1] #[2:-1] Usuwa dwa pierwsze znaki stringa
    if password == _password:
        return True
    return False
