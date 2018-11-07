# coding: utf-8

from flask import Flask
from flask import session
from flask import request
from flask import render_template
from flask import redirect
from flask import send_from_directory

import csv
import os

app = Flask(__name__)
app.secret_key = b'35325fsdgsdg4gsd3fsge'

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
        path = 'userfiles/' + str(user) + '/'
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
        else:
            file2 = ''
        if len(files) >= 4:
            file3 = files[3]
        else:
            file3 = ''
        if len(files) >= 5:
            file4 = files[4]
        else:
            file4 = ''

        return render_template('home.html', user=user, file0=file0, file1=file1, file2=file2, file3=file3, file4=file4, path0=path0, path1=path1)
    else:
        return redirect('/pogodzip/login/login')

#Trasownik do wylogowywania się
@app.route('/pogodzip/login/logout')
def logout():
    session.pop('user', None)
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

    with open('users', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        #Sprawdzanie wprowadzonych danych z zdefioniowanymi w pliku CSV
        for row in reader:
            if _login == row['login'] and _password == row['pass']:
                session['user'] = _login
                return redirect('/pogodzip/login/home')
    return redirect('/pogodzip/login/login')

#Trasownik do pobierania plików
@app.route('/pogodzip/login/userfiles/<path:file0>', methods=['GET', 'POST'])
def download(file0):
    return send_from_directory(directory='userfiles', filename=file0)

#Trasownik do pliku .CSS
@app.route('/pogodzip/login/static/style.css', methods=['GET'])
def downloadCss():
    return send_from_directory(directory='static', filename='style.css')

#Trasownik do wysyłania plików
@app.route('/pogodzip/login/upload')
@app.route('/pogodzip/login/upload.html')
def upload():
    return render_template('upload.html')

#Trasownik do metody obsługującej wysyłanie piku
@app.route('/pogodzip/login/uploading', methods=['POST'])
def uploading():
    if session.get('user'):
        user = session['user']
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
