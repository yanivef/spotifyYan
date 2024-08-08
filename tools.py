import psycopg2 as ps
from db import DB_HOST, DB_PASS, DB_PORT, DB_USER, DB_NAME

SECRET_KEY = 'blabla'
EMAIL_PASSWORD_QUERY = """ SELECT email, password FROM users WHERE email = %s AND password = %s """
EMAIL_QUERY =""" SELECT email FROM users WHERE email = %s """
NAME_QUERY =""" SELECT fname, lname FROM users WHERE email = %s """

INSERT_USER_QUERY = """INSERT INTO users VALUES(%s, %s, %s, %s)"""

conn = ps.connect(dbname=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT)

cur = conn.cursor()


def handle_login(email, password):
    cur.execute(EMAIL_PASSWORD_QUERY, (email, password))
    conn.commit()
    if cur.fetchall():
        return True

    return False


def handle_user_exists(email):
    cur.execute(EMAIL_QUERY, (email,))
    conn.commit()
    if cur.fetchall():
        return True     # user already exists

    return False        # user doesnt exists


def handle_user_submit(fname, lname, email, password):
    cur.execute(INSERT_USER_QUERY, (email, fname, lname, password))
    conn.commit()


def get_user_full_name(email):
    cur.execute(NAME_QUERY, (email,))
    conn.commit()
    
    lst = [*cur.fetchone()]
    return lst[0] + ' ' + lst[1]

