import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
chat_id INTEGER
)
''')
conn.commit()
conn.close()