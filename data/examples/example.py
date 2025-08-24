import os, sqlite3

def run(user_input, db_path="app.db"):
    # vulnerable on purpose for the demo
    q = f"SELECT * FROM users WHERE name = '{user_input}'"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(q)
    return cur.fetchall()
