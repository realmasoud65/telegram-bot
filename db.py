import sqlite3
import time

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    last_request INTEGER
)
""")
conn.commit()

def can_get_config(user_id, limit_minutes):
    cursor.execute(
        "SELECT last_request FROM users WHERE user_id=?",
        (user_id,)
    )
    row = cursor.fetchone()
    now = int(time.time())

    if row is None:
        cursor.execute(
            "INSERT INTO users (user_id, last_request) VALUES (?, ?)",
            (user_id, now)
        )
        conn.commit()
        return True

    last = row[0]
    if now - last >= limit_minutes * 60:
        cursor.execute(
            "UPDATE users SET last_request=? WHERE user_id=?",
            (now, user_id)
        )
        conn.commit()
        return True

    return False
