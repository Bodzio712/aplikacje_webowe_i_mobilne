# coding: utf-8

from flask import Flask
from flask import Response
from flask import session
from flask import request
from flask import render_template
from flask import redirect
from flask import send_from_directory
from flask import url_for
from flask import jsonify

from authlib.flask.client import OAuth
from functools import wraps
from six.moves.urllib.parse import urlencode
from werkzeug.utils import secure_filename

import csv
import os
import uuid
import jwt
import datetime
import redis

#Wstępna konfiguracja aplikacji
app = Flask(__name__)
if __name__ == "__main__":
    app.run(ssl_context='adhoc')
    app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
    )

#Wczytywanie kluczy z pliku sec.cfg
with open ('sec.cfg', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        if row['key'] == 'client_secret':
            auth_client_secret = row['value']
        if row['key'] == 'jwt_secret_key':
            jwt_secret_key = row['value']


#Tworzenie obiektu OAyth
oauth = OAuth(app)

#Tworzenie obiektu z kluczami klienta
auth0 = oauth.register(
    'PAMiW',
    client_id='eWWsg8LQ0XXlhWAbb5qKGMj6nwsGzHkz',
    client_secret=auth_client_secret,
    api_base_url='https://pogodzip.eu.auth0.com',
    access_token_url='https://pogodzip.eu.auth0.com/oauth/token',
    authorize_url='https://pogodzip.eu.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)

#Trasownik do wywoływania Autha
@app.route('/pogodzip/webapp/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    sid = str(uuid.uuid4())
    #Wpisywanie danych do tokena JWT
    token_elems = {
        'login': userinfo['sub'],
        'sid': sid,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }
    #Generowanie tokena
    token = str(jwt.encode(token_elems, jwt_secret_key))[2:-1]
    #Dodawanie sesji użytkownika do bazy Redis
    r.hset('pogodzip:webapp:'+sid, 'login', userinfo['sub'])
    session['user'] = userinfo['sub']
    session['sid'] = sid
    session['token'] = token
    #r.delete('pogodzip:webapp:paths')
    if str(r.hget('pogodzip:webapp:paths', userinfo['sub']))[2:-1] == 'n':
        #Generowanie SIDa do uniezależneinia nazwy katalogu użytkownika od nazwy użytkownika
        sid = str(uuid.uuid4())
        #Generowanie katalogu użytkownika na podstawie SIDa
        path = "userfiles/"+sid
        os.makedirs(path)
        #Dodawanie ścieżki do bazy danych, która przechowuje dane o powiązaniach nazwy użytkownika z katalogiem
        r.hset('pogodzip:webapp:paths', userinfo['sub'], path)

    return redirect('/pogodzip/webapp/index')


def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)
  return decorated

@app.route('/pogodzip/webapp/loginAuth')
def authenticate():
    return auth0.authorize_redirect(redirect_uri='https://pi.iem.pw.edu.pl/pogodzip/webapp/callback', audience='https://pogodzip.eu.auth0.com/userinfo')

app.secret_key = b'35325fsdgsdg4gsd3fsge'

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
@requires_auth
def home():
    #Wyciąganie danych o użytkowniku
    user = session['user']
    token = session['token']
    userfiles = str(r.hget('pogodzip:webapp:paths', user))[2:-1]
    path = '/pogodzip/dl/' + userfiles + '/'
    pathWebapp = '/pogodzip/webapp/' + userfiles + '/'
    files = os.listdir(userfiles)

    filesDisplay=["","","","",""]
    paths=["","","","",""]
    pathsWebapp=["","","","",""]

    data = [["","",""],["","",""],["","",""],["","",""],["","",""]]

    #Zapisywanie nazw plików użytkownika
    i = 0
    for x in filesDisplay:
        if len(files) >= i+1:
            data[i][0] = files[i]
            filesDisplay[i] = files[i]
            i += 1
                

    #Zapisywanie ścieżek uźytkownika        
    i = 0
    for x in paths:
        if len(files) >= i+1:
            paths[i] = path + filesDisplay[i]
            data[i][1] = paths[i]
            i += 1

    #Zapisywanie ścieżek do webapp
    i = 0
    for x in pathsWebapp:
        if len(files) >= i+1:
            pathsWebapp[i] = pathWebapp + filesDisplay[i]
            data[i][2] = pathsWebapp[i]
            i += 1

    #Renderowanie strony z plikami do pobrania
    return render_template('home.html', user=user, token=token, data=data)

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

#Trasownik do pliku CSS
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
