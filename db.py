import psycopg2 as ps
import os
from tools import configure

configure()  # load env

try:
    conn = ps.connect(dbname=os.getenv('DB_NAME'), host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
                      password=os.getenv('DB_PASS'), port=os.getenv('DB_PORT'))

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
                    email VARCHAR(255) PRIMARY KEY,
                    fname VARCHAR(255) NOT NULL,
                    lname VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
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
