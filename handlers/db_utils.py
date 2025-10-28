import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        nickname TEXT,
        score INTEGER DEFAULT 0,
        balance INTEGER DEFAULT 0,
        time_spent INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def set_nickname(user_id, nickname):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO users (user_id, nickname)
                 VALUES (?, ?)
                 ON CONFLICT(user_id) DO UPDATE SET nickname=excluded.nickname
              """, (user_id, nickname))
    conn.commit()
    conn.close()

def update_user(user_id, score, balance, time_spent):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE users 
                 SET score=?, balance=?, time_spent=? 
                 WHERE user_id=?""", (score, balance, time_spent, user_id))
    conn.commit()
    conn.close()

def get_top10():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nickname, score, balance FROM users ORDER BY score DESC, balance DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

# --- BALANCE FUNCTIONS ---
def get_balance(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def set_balance(user_id, balance):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Əvvəlcə istifadəçi mövcuddurmu?
    c.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    exists = c.fetchone()
    if exists:
        c.execute("UPDATE users SET balance=? WHERE user_id=?", (balance, user_id))
    else:
        c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?) ", (user_id, balance))
    conn.commit()
    conn.close()
