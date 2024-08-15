import psycopg2 as ps
import os
from dotenv import load_dotenv


# load env
def configure():
    load_dotenv()

configure()


EMAIL_PASSWORD_QUERY = """ SELECT email, password FROM users WHERE email = %s AND password = %s """
EMAIL_QUERY = """ SELECT email FROM users WHERE email = %s """
NAME_QUERY = """ SELECT fname || ' ' || lname FROM users WHERE email = %s """
GET_ID_QUERY = """ SELECT user_id FROM users WHERE email = %s """
GET_USER_PLAYLISTS_QUERY = """ SELECT playlist_id, playlist_name FROM playlists WHERE user_id = %s """
GET_OTHER_USERS_QUERY = """ SELECT user_id, fname || ' ' || lname FROM users WHERE user_id != %s """

INSERT_USER_QUERY = """ INSERT INTO users (email, fname, lname, password) VALUES(%s, %s, %s, %s)"""
INSERT_USER_PLAYLIST_QUERY = """ INSERT INTO playlists VALUES(%s, %s, %s) """

REMOVE_PLAYLIST_QUERY = """ DELETE FROM playlists WHERE playlist_id = %s AND user_id = %s """

CLEAR_USER_PLAYLISTS_QUERY = """ DELETE FROM playlists WHERE user_id = %s """


conn = ps.connect(dbname=os.getenv('DB_NAME'), host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), port=os.getenv('DB_PORT'))

cur = conn.cursor()


def handle_login(email, password):
    cur.execute(EMAIL_PASSWORD_QUERY, (email, password))
    conn.commit()
    if cur.fetchall():
        return True

    return False


def handle_user_exists(email):
    try:
        cur.execute(EMAIL_QUERY, (email,))
        conn.commit()
        if cur.fetchall():
            return True     # user already exists

        return False        # user doesnt exists

    except Exception as e:
        print(f'Something went wrong, error: {e}')


def handle_user_submit(fname, lname, email, password):
    cur.execute(INSERT_USER_QUERY, (email, fname, lname, password))
    conn.commit()


def get_user_full_name(email):
    try:
        cur.execute(NAME_QUERY, (email,))
        conn.commit()

        full_name = cur.fetchone()[0]

        return full_name

    except Exception as e:
        print(f'Cannot fetch user full name, error: {e}')


def get_user_id(email):
    try:
        cur.execute(GET_ID_QUERY, (email, ))
        conn.commit()

        user_id = cur.fetchone()[0]
        return user_id

    except Exception as e:
        print(f'Cannot fetch user id, error: {e}')


def insert_user_playlists(playlist_id, user_id, playlist_name):
    try:
        cur.execute(INSERT_USER_PLAYLIST_QUERY, (playlist_id, user_id, playlist_name))
        conn.commit()

    except Exception as e:
        print(f'User playlist insertion failed, error: {e}')


def get_user_db_playlists(user_id):
    try:
        cur.execute(GET_USER_PLAYLISTS_QUERY, (user_id, ))
        conn.commit()

        playlists = cur.fetchall()
        # if there are any playlists
        if playlists:
            playlists_dict = {}
            for i in range(len(playlists)):
                pl_id = playlists[i][0]
                pl_name = playlists[i][1]
                playlists_dict[pl_id] = pl_name

            return playlists_dict

        return None

    except Exception as e:
        print(f"Cant generate user's playlist, error: {e}")


def remove_playlist(playlist_id, user_id):
    cur.execute(REMOVE_PLAYLIST_QUERY, (playlist_id, user_id))
    conn.commit()


def update_user_playlists(playlists, user_id):
    playlists_db = get_user_db_playlists(user_id)

    # clear DB if user has no playlists
    if not playlists:
        cur.execute(CLEAR_USER_PLAYLISTS_QUERY, (user_id, ))
        conn.commit()
        return
    # if DB is empty -> add all playlists from spotify profile
    if not playlists_db:
        for playlist_id, playlist_name in playlists.items():
            insert_user_playlists(playlist_id, user_id, playlist_name)
        return

    # insert new playlists to DB
    for playlist_id, playlist_name in playlists.items():
        if playlist_id not in playlists_db.keys():
            insert_user_playlists(playlist_id, user_id, playlist_name)

    # remove playlists from DB if they removed from updated spotify user profile
    for playlist_id, playlist_name in playlists_db.items():
        if playlist_id not in playlists.keys():
            remove_playlist(playlist_id, user_id)


# get all other users -> all users except current user
def get_other_users(user_id):
    try:
        cur.execute(GET_OTHER_USERS_QUERY, (user_id, ))
        conn.commit()

        lst = [*cur.fetchall()]

        # if there are any other users
        if lst:
            user_details = {}       # KEY -> user id,    VALUE -> user full name
            for details in lst:
                user__id = details[0]
                full_name = details[1]
                if user__id not in user_details:
                    user_details[user__id] = full_name

            return user_details

        return None

    except Exception as e:
        print(f'Cant fetch other users, error: {e}')
