from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import db_init
from tools import (handle_login, handle_user_exists, handle_user_submit, get_user_full_name, configure,
                   update_user_playlists, get_other_users, get_user_db_playlists, get_user_id, is_valid_registration,
                   check_playlists_difference, get_tracks_from_db_in_pl)
from spotify import get_playlists, generate_redirect_to_spotify, get_access_token, create_sp
from functools import wraps
import os
import hashlib
from datetime import datetime, timedelta, timezone


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def generate_tracks(func):
    @wraps(func)
    def dec_func(*args, **kwargs):
        if 'access_token' in session and 'first_login' not in session:
            access_token = session['access_token']
            sp = create_sp(access_token)          # creates spotify obj for user base on his access token
            user_id = session['user_id']
            playlists = get_playlists(sp)         # current actual playlists
            update_user_playlists(sp, playlists, user_id)  # update DB playlists
            session['first_login'] = True


            # g.tracks = get_tracks_from_db_in_pl(user_id)        # store tracks from DB every home request

            # if check_playlists_difference(user_id, playlists):
            #     update_user_playlists(sp, playlists, user_id)  # update DB playlists
            #     g.tracks = get_tracks_from_db_in_pl(user_id)

        return func(*args, **kwargs)
    return dec_func


def login_req(func):
    @wraps(func)
    def dec_func(*args, **kwargs):
        if 'logged_in' not in session or 'email' not in session or 'full_name' not in session or 'user_id' not in session:
            flash('You need to be logged in', 'danger')
            return redirect(url_for('login'))
        # check for token expiration
        if 'access_token' in session and 'token_expires' in session:
            token_expires = session['token_expires']
            current_time = datetime.now().replace(tzinfo=timezone.utc)  # get current time, same timezone offset (UTC)

            if current_time >= token_expires:
                session.clear()                                     # clear session
                flash('Login expired!', category='danger')
                return redirect(url_for('login'))                   # user need to log in again, token expired

        return func(*args, **kwargs)
    return dec_func


@app.route('/')
def index():
    session.clear()    # clears session when reopening app
    return render_template('index.html')


@app.route('/home')
@login_req
@generate_tracks
def home():
    user_id = session['user_id']
    tracks = [get_tracks_from_db_in_pl(user_id)]        # need to wrap in list because we are passing a json obj
    playlists = get_user_db_playlists(user_id)
    return render_template('home.html', playlists=playlists, tracks=tracks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if request.method == 'POST' and email and password:
        password = hashlib.sha256(password.encode()).hexdigest()    # hash the password
        # check credentials in DB
        logged_in = handle_login(email, password)
        if logged_in:
            session['logged_in'] = True
            session['email'] = email
            session['full_name'] = get_user_full_name(email)
            session['user_id'] = get_user_id(email)

            url_spotify_login = generate_redirect_to_spotify()      # gets url to redirect user in order to get scope permissions
            return redirect(url_spotify_login)                      # redirects user to the spotify login url
        else:
            flash('Invalid credentials!', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    fname = request.form.get('fname-reg')
    lname = request.form.get('lname-reg')
    password = request.form.get('password-reg')
    password = hashlib.sha256(password.encode()).hexdigest()    # hash the password
    email = request.form.get('email-reg')

    if is_valid_registration(fname, lname, email, password):
        if request.method == 'POST' and fname and lname and password and email:
            is_exist = handle_user_exists(email)        # check if user already exists
            if is_exist:
                flash('Email is already taken!', 'danger')
                return render_template('register.html')

            else:
                # USER DOESNT EXIST, ADD HIM TO DB
                handle_user_submit(fname, lname, email, password)
                return redirect(url_for('login'))

    flash('Please make sure all fields are filled', 'danger')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# generates list of all other users from DB
@app.route('/other-playlists')
@login_req
def other_playlists():
    user_id = session['user_id']        # there is a check for 'user_id' in session in the 'login_req' decorator
    users_details = get_other_users(user_id)
    return render_template('other-playlists.html', users_details=users_details)


# gets the details from the submitted form -> gets the details of the 'other user' we chose
@app.route('/generate-other-pl', methods=['POST'])
@login_req
def generate_other_pl():
    if request.method == 'POST':
        other_user_id, other_user_fullname = next(iter(request.form.items()))   # get the id, full name. no need to use FOR loop,
                                                                                # there is only one item
        session['other_user_fullname'] = other_user_fullname
        session['other_user_id'] = other_user_id

        return redirect(url_for('other_user_pl'))

    return redirect(url_for('other_playlists'))


# render the page with the 'other user' playlists
@app.route('/other-user-pl', methods=['GET', 'POST'])
@login_req
def other_user_pl():
    if 'other_user_fullname' not in session or 'other_user_id' not in session:
        return redirect(url_for('other_playlists'))
    other_user_id, other_user_fullname = session['other_user_id'], session['other_user_fullname']
    other_user_playlists = get_user_db_playlists(other_user_id)
    base_url = 'https://open.spotify.com/playlist/'     # need to concat playlist id

    return render_template('other-user-playlists.html', other_user_id=other_user_id,
                           other_user_fullname=other_user_fullname, other_user_playlists=other_user_playlists,
                           base_url=base_url)


# sync connected user playlists and tracks
@app.route('/sync-playlists', methods=['POST'])
@login_req
def sync_playlists():
    if 'access_token' in session:
        access_token = session['access_token']
        sp = create_sp(access_token)  # creates spotify obj for user base on his access token
        user_id = session['user_id']
        playlists = get_playlists(sp)  # current actual playlists

        update_user_playlists(sp, playlists, user_id)
        return redirect(url_for('home'))


# spotify will send response to callback route -> base on the route set in the developer dashboard on spotify website
@app.route('/callback')
def callback():
    code = request.args.get('code')                            # get the code from the spotify response
    access_token, token_expires = get_access_token(code)       # convert code to access token, get token access, token expiration
    session['access_token'] = access_token                     # store access token in session
    expiration_time = datetime.now() + timedelta(seconds=token_expires)     # current time + the token expiration time = expiration time of the token
    session['token_expires'] = expiration_time                 # store token expiration time in session

    return redirect(url_for('home'))

if __name__ == '__main__':
    configure()     # load env
    db_init()
    app.run(debug=True)
