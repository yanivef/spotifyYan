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
GET_USER_DB_TRACKS = """ SELECT playlist_id, track_name FROM tracks WHERE user_id = %s """


INSERT_USER_QUERY = """ INSERT INTO users (email, fname, lname, password) VALUES(%s, %s, %s, %s)"""
INSERT_USER_PLAYLIST_QUERY = """ INSERT INTO playlists VALUES(%s, %s, %s) """
INSERT_TRACKS_QUERY = """ INSERT INTO tracks VALUES(%s, %s, %s, %s) """


REMOVE_PLAYLIST_QUERY = """ DELETE FROM playlists WHERE playlist_id = %s AND user_id = %s """

CLEAR_USER_PLAYLISTS_QUERY = """ DELETE FROM playlists WHERE user_id = %s """


conn = ps.connect(dbname=os.getenv('DB_NAME'), host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), port=os.getenv('DB_PORT'))

cur = conn.cursor()


def is_valid_registration(fname, lname, email, password):
    if not fname or not lname or not email or not password:
        # error..
        return False
    if fname.isnumeric() or lname.isnumeric() or email.isnumeric():
        # error..
        return False
    if len(fname) < 2 or len(lname) < 2 or len(email) < 8 or len(password) < 4:
        # error
        return False

    return True


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


# get current tracks in playlist (from spotify), returns dict of KEY-> track id,       VALUE-> track name
def get_tracks_in_playlist_new(sp, playlist_id):
    details = sp.playlist_tracks(playlist_id)

    if not details:
        return None

    tracks_detail = {}              # KEY -> track id,      VALUE -> track name
    for item in details['items']:
        track_id = item['track']['id']
        track_name = item['track']['name']
        if track_id not in tracks_detail:
            tracks_detail[track_id] = track_name

    return tracks_detail


def insert_user_playlists(sp, playlist_id, user_id, playlist_name):
    try:
        cur.execute(INSERT_USER_PLAYLIST_QUERY, (playlist_id, user_id, playlist_name))
        track_details = get_tracks_in_playlist_new(sp, playlist_id)
        if track_details:
            for track_id, track_name in track_details.items():
                cur.execute(INSERT_TRACKS_QUERY, (track_id, playlist_id, user_id, track_name))
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


def update_user_playlists(sp, playlists, user_id):
    playlists_db = get_user_db_playlists(user_id)

    # clear DB if user has no playlists
    if not playlists:
        cur.execute(CLEAR_USER_PLAYLISTS_QUERY, (user_id, ))
        conn.commit()
        return
    # if DB is empty -> add all playlists from spotify profile
    if not playlists_db:
        for playlist_id, playlist_name in playlists.items():
            insert_user_playlists(sp, playlist_id, user_id, playlist_name)
        return

    # insert new playlists to DB
    for playlist_id, playlist_name in playlists.items():
        # if playlist was already in the DB but a change was made in tracks aspect
        if playlist_id in playlists_db.keys():
            remove_playlist(playlist_id, user_id)
            insert_user_playlists(sp, playlist_id, user_id, playlist_name)

        if playlist_id not in playlists_db.keys():
            insert_user_playlists(sp, playlist_id, user_id, playlist_name)

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
        return None


# returns True if there is difference between PL in DB and PL in spotify, otherwise False
# def check_playlists_difference(user_id, playlists):
#     current_pl_db = get_user_db_playlists(user_id)            # get user playlists from DB
#     if current_pl_db and playlists:
#         current_pl_db_list = {*current_pl_db.keys()}          # make a set of playlists id from DB
#         current_pl_spotify = {*playlists.keys()}              # make a set of updated playlists id
#         diff = (current_pl_db_list != current_pl_spotify)     # check if there is a difference between DB and SPOTIFY
#
#         if diff:
#             return True
#
#     # in case one of them is empty
#     elif playlists or current_pl_db:
#         return True
#
#     return False


# get user tracks and return as dict: KEY-> playlist_id     VALUE-> [track_name], track names as list
def get_tracks_from_db_in_pl(user_id):
    try:
        cur.execute(GET_USER_DB_TRACKS, (user_id, ))
        conn.commit()

        tracks_detail = cur.fetchall()
        if tracks_detail:
            details = {}
            for item in tracks_detail:
                playlist_id = item[0]
                track_name = item[1]
                if playlist_id not in details:
                    details[playlist_id] = [track_name]
                else:
                    details[playlist_id].append(track_name)
            return details
        return None

    except Exception as e:
        print(f'Couldnt get tracks from DB,error: {e}')
        return None
