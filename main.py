from flask import Flask, render_template, request, redirect, url_for, session, flash
from tools import (handle_login, handle_user_exists, handle_user_submit, get_user_full_name, configure,
                   update_user_playlists, get_other_users, get_user_db_playlists)
from spotify import get_playlists, tracks_in_playlists, generate_redirect_to_spotify, get_access_token, create_sp
from functools import wraps
import os
import hashlib


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def login_req(func):
    @wraps(func)
    def dec_func(*args, **kwargs):
        if 'logged_in' not in session or 'email' not in session or 'full_name' not in session:
            flash('You need to be logged in', 'danger')
            return redirect(url_for('login'))

        # if sp_created is True, no need to create again
        if 'access_token' in session and 'sp_created' not in session:
            access_token = session['access_token']
            sp = create_sp(access_token)        # creates spotify obj for user base on his access token
            session['sp_created'] = True        # stores in session True if sp obj created

            # update user's playlists on every log
            user_email = session['email']
            playlists = get_playlists(sp)                   # current updated playlists
            update_user_playlists(playlists, user_email)    # update DB playlists

            if 'tracks' not in session:
                session['tracks'] = tracks_in_playlists(sp)
        return func(*args, **kwargs)
    return dec_func


@app.route('/')
def index():
    session.clear()    # clears session when reopening app
    return render_template('index.html')


@app.route('/home')
@login_req
def home():
    access_token = session['access_token']
    sp = create_sp(access_token)
    tracks = [session['tracks']]
    playlists = get_playlists(sp)
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
    if request.method == 'POST' and fname and lname and password and email:
        is_exist = handle_user_exists(email)        # check if user already exists
        if is_exist:
            flash('Email is already taken!', 'danger')
        else:
            # USER DOESNT EXIST, SUBMIT HIM TO DB
            handle_user_submit(fname, lname, email, password)
            # HANDLE SESSION FOR NEW USER -> AFTER REGISTER HE IS LOGGED IN
            session['logged_in'] = True
            session['email'] = email
            session['full_name'] = f'{fname} {lname}'

    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# generates list of all other users from DB
@app.route('/other-playlists')
@login_req
def other_playlists():
    user_email = session['email']               # there is a check for 'email' in session in the 'login_req' decorator
    users_details = get_other_users(user_email)

    return render_template('other-playlists.html', users_details=users_details)


# gets the details from the submitted form -> gets the details of the 'other user' we chose
@app.route('/generate-other-pl', methods=['POST'])
@login_req
def generate_other_pl():
    if request.method == 'POST':
        other_user_email, other_user_fullname = next(iter(request.form.items()))     # get the email, full name. no need to use for loop,
                                                                                     # there is only one item
        session['other_user_email'] = other_user_email
        session['other_user_fullname'] = other_user_fullname

        return redirect(url_for('other_user_pl'))

    return redirect(url_for('other_playlists'))


# render the page with the 'other user' playlists
@app.route('/other-user-pl', methods=['GET', 'POST'])
@login_req
def other_user_pl():
    if 'other_user_fullname' not in session or 'other_user_email' not in session:
        return redirect(url_for('other_playlists'))
    other_user_email, other_user_fullname = session['other_user_email'], session['other_user_fullname']
    other_user_playlists = get_user_db_playlists(other_user_email)

    return render_template('other-user-playlists.html', other_user_email=other_user_email,
                           other_user_fullname=other_user_fullname, other_user_playlists=other_user_playlists)


# spotify will send response to callback route -> base on the route set in the developer dashboard on spotify website
@app.route('/callback')
def callback():
    code = request.args.get('code')             # get the code from the spotify response
    access_token = get_access_token(code)       # convert code to access token
    session['access_token'] = access_token      # store access token in session

    return redirect(url_for('home'))

if __name__ == '__main__':
    configure()     # load env
    app.run(debug=True)
