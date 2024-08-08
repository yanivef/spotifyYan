from flask import Flask, render_template, request, redirect, url_for, session, flash
from tools import handle_login, handle_user_exists, handle_user_submit, SECRET_KEY, get_user_full_name
from spotify import get_playlists, tracks_in_playlists
from functools import wraps
import hashlib


app = Flask(__name__)
app.secret_key = SECRET_KEY


def login_req(func):
    @wraps(func)
    def dec_func(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to be logged in', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return dec_func


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
@login_req
def home():
    tracks = [tracks_in_playlists()]
    return render_template('home.html', playlists=get_playlists(), tracks=tracks)


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
            # flash('Logged In Successfully!', 'success')
            return redirect(url_for('home'))
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


if __name__ == '__main__':
    app.run(debug=True)