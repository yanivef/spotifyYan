import requests
import json
import os
import spotipy
from tools import configure
import urllib.parse
from flask import Flask, request, redirect, url_for, session
import base64

configure()     # loads env


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
sp_auth = spotipy.SpotifyOAuth(client_secret=os.getenv('CLIENT_SECRET'),
                               client_id=os.getenv('CLIENT_ID'),
                               redirect_uri=os.getenv('REDIRECT_URI'),
                               scope=os.getenv('SCOPE'))


def get_token():
    url = 'https://accounts.spotify.com/authorize?'
    query = {
        'response_type': 'code',
        'client_id': os.getenv('CLIENT_ID'),
        'redirect_uri': os.getenv('REDIRECT_URI'),
        'scope': os.getenv('SCOPE'),
        'show_dialog': True
    }
    res = requests.get(url + urllib.parse.urlencode(query))
    return res


@app.route('/')
def index():
    session.clear()
    return '<h1>Hello</h1>'


@app.route('/testing')
def testing():
    print(session['token_access'])
    token_access = session['token_access']
    sp = spotipy.Spotify(auth=token_access)
    print(sp)
    print(sp.current_user())
    return '<h1>WORK</h1>'

@app.route('/home')
def home():
    url = 'https://accounts.spotify.com/authorize?'
    query = {
        'response_type': 'code',
        'client_id': os.getenv('CLIENT_ID'),
        'redirect_uri': os.getenv('REDIRECT_URI'),
        'scope': os.getenv('SCOPE'),
        'show_dialog': True
    }
    return redirect(url + urllib.parse.urlencode(query))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv('REDIRECT_URI')
    }

    # Get client_id and client_secret from environment variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    # Encode client_id and client_secret in Base64
    credentials = f'{client_id}:{client_secret}'
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Authorization': f'Basic {encoded_credentials}'}
    response = requests.post(token_url, data=token_data, headers=headers)
    token_info = response.json()
    print('the token info is: ', token_info)
    token_access = token_info['access_token']
    session['token_access'] = token_access

    headers = {
        'Authorization': f'Bearer {token_access}'
    }

    # Make a request to the /v1/me endpoint
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    print(response)
    return redirect(url_for('testing'))


if __name__ == '__main__':
    app.run(debug=True)
