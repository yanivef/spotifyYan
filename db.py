import psycopg2 as ps
import hashlib

DB_NAME = 'postgres'
DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_PASS = '1107413a'
DB_PORT = 5432

try:
    conn = ps.connect(dbname=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT)
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
