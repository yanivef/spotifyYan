import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

CLIENT_ID = '5627cc5063364eb999c84a473cbf23be'
CLIENT_SECRET = 'd6b78ff455b34433a30a4337b52edb0c'
REDIRECT_URI = 'http://localhost:3000'
SCOPE = 'user-library-read playlist-read-private'


client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_secret=CLIENT_SECRET,
                                               client_id=CLIENT_ID,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))


def get_playlists():
    playlists = sp.current_user_playlists(limit=20)     # limit - 20, gets up to 20 playlists
    # playlists['items'] = []       # check case for user without playlists
    if not playlists['items']:      # if user has no playlists -> playlists['items'] is empty list
        return []

    playlists_dict = {}     # KEY -> playlist id,     VALUE -> playlist name
    for playlist in playlists['items']:
        if playlist['id'] not in playlists_dict:
            playlists_dict[playlist['id']] = playlist['name']
    return playlists_dict


def get_tracks_in_playlist(playlist_id):
    tracks = sp.playlist_items(playlist_id)
    list_of_tracks = []
    for track in tracks['items']:
        list_of_tracks.append(track['track']['name'])
    return list_of_tracks


def tracks_in_playlists():
    playlists_dict = get_playlists()
    if not playlists_dict:      # the return value from get_playlists() was empty list
        return
    dict_of_tracks = {}     # KEY -> playlist id,   VALUE -> playlist tracks (as list)
    for playlist_id in playlists_dict.keys():
        dict_of_tracks[playlist_id] = get_tracks_in_playlist(playlist_id)
    return dict_of_tracks
