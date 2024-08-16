import psycopg2 as ps
import os
from tools import configure


def db_init():
    configure()  # load env

    try:
        conn = ps.connect(dbname=os.getenv('DB_NAME'), host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
                          password=os.getenv('DB_PASS'), port=os.getenv('DB_PORT'))

        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                        user_id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        fname VARCHAR(255) NOT NULL,
                        lname VARCHAR(255) NOT NULL,
                        password VARCHAR(255) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                        playlist_id VARCHAR(255),
                        user_id INT,
                        playlist_name VARCHAR(255) NOT NULL,
                        
                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                        PRIMARY KEY (user_id, playlist_id)
            );
        """)

        conn.commit()

    except Exception as e:
        print(f'Connection to DB failed, error: {e}')

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()
