from tools import get_db_connection


def db_init():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
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

                cur.execute("""
                            CREATE TABLE IF NOT EXISTS tracks (
                                track_id VARCHAR(255) NOT NULL,
                                playlist_id VARCHAR(255) NOT NULL,
                                user_id INT NOT NULL,
                                track_name VARCHAR(255) NOT NULL,
                                
                                PRIMARY KEY (track_id, playlist_id, user_id),
                                FOREIGN KEY (user_id, playlist_id) REFERENCES playlists(user_id, playlist_id) ON DELETE CASCADE
                            );
        
                        """)

                conn.commit()

    except Exception as e:
        print(f'Connection to DB failed, error: {e}')

