import os
from dotenv import load_dotenv

load_dotenv()       # load env

# APP stuff
SECRET_KEY = 'SECRET_KEY'
ACCESS_TOKEN = 'access_token'
FIRST_LOGIN = 'first_login'
USER_ID = 'user_id'
LOGGED_IN = 'logged_in'
EMAIL = 'email'
PASSWORD = 'password'
FULL_NAME = 'full_name'
TOKEN_EXPIRES = 'token_expires'
OTHER_USER_ID = 'other_user_id'
OTHER_USER_FULLNAME = 'other_user_fullname'

# flash messages
LOGIN_REQ_MSG = 'You need to be logged in'
LOGIN_EXP_MSG = 'Login expired!'
INVALID_CRED_MSG = 'Invalid credentials!'
EMAIL_EXISTS_MSG = 'Email is already taken!'
EMPTY_CRED_FIELD = 'Please ensure that all fields are properly filled out.'

# DB queries
EMAIL_PASSWORD_QUERY = """ SELECT email, password FROM users WHERE email = %s AND password = %s """
EMAIL_QUERY = """ SELECT email FROM users WHERE email = %s """
NAME_QUERY = """ SELECT fname || ' ' || lname FROM users WHERE email = %s """
GET_ID_QUERY = """ SELECT user_id FROM users WHERE email = %s """
GET_USER_PLAYLISTS_QUERY = """ SELECT playlist_id, playlist_name FROM playlists WHERE user_id = %s """
GET_OTHER_USERS_QUERY = """ SELECT user_id, fname || ' ' || lname FROM users WHERE user_id != %s """
GET_USER_DB_TRACKS = """ SELECT playlist_id, track_name FROM tracks WHERE user_id = %s """

INSERT_USER_QUERY = """ INSERT INTO users (email, fname, lname, password) VALUES(%s, %s, %s, %s)"""
INSERT_USER_PLAYLIST_QUERY = """ INSERT INTO playlists VALUES(%s, %s, %s) """
INSERT_TRACKS_QUERY = """ INSERT INTO tracks VALUES(%s, %s, %s, %s) """

REMOVE_PLAYLIST_QUERY = """ DELETE FROM playlists WHERE playlist_id = %s AND user_id = %s """
CLEAR_USER_PLAYLISTS_QUERY = """ DELETE FROM playlists WHERE user_id = %s """


# DB stuff
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')


# SPOTIFY stuff
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = os.getenv('SCOPE')
