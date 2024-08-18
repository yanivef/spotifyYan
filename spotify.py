import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from tools import configure
import requests
import urllib.parse
import base64


configure()  # load env

CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = os.getenv('SCOPE')


# init SpotifyOAuth with spotify developer credentials
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)


# redirects user to spotify login page
def generate_redirect_to_spotify():
    url = 'https://accounts.spotify.com/authorize?'
    query = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'show_dialog': True
    }
    res = (url + urllib.parse.urlencode(query))
    return res


# gets access_token by code given after the user logged in (by the redirect_to_spotify function)
def get_access_token(code):
    token_url = 'https://accounts.spotify.com/api/token'

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }

    # encode credentials and format in order to pass it
    encoded_credentials = base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()

    headers = {'Content-type': 'application/x-www-form-urlencoded',
               'Authorization': f'Basic {encoded_credentials}'}

    response = requests.post(token_url, data=token_data, headers=headers)
    token_info = response.json()
    token_access = token_info.get('access_token')
    token_expires = token_info.get('expires_in')
    return token_access, token_expires


def create_sp(token_access):
    sp = spotipy.Spotify(auth=token_access)
    return sp


def get_playlists(sp):
    # if sp is None
    if not sp:
        return []
    playlists = sp.current_user_playlists(limit=20)     # limit - 20, gets up to 20 playlists
    if not playlists.get('items'):  # if user has no playlists -> playlists['items'] is empty list
        return []

    playlists_dict = {}     # KEY -> playlist id,     VALUE -> playlist name
    for playlist in playlists['items']:
        if playlist['id'] not in playlists_dict:
            playlists_dict[playlist['id']] = playlist['name']
    return playlists_dict

#
# def get_tracks_in_playlist(sp, playlist_id):
#     tracks = sp.playlist_items(playlist_id)
#     list_of_tracks = []
#
#     for track in tracks['items']:
#         list_of_tracks.append(track['track']['name'])
#
#     return list_of_tracks

#
# def tracks_in_playlists(sp):
#     playlists_dict = get_playlists(sp)
#     if not playlists_dict:      # the return value from get_playlists() was empty list
#         return
#     dict_of_tracks = {}     # KEY -> playlist id,   VALUE -> playlist tracks (as list)
#
#     for playlist_id in playlists_dict.keys():
#         dict_of_tracks[playlist_id] = get_tracks_in_playlist(sp, playlist_id)
#     return dict_of_tracks
