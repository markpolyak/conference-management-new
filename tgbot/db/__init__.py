import sqlite3


CON = sqlite3.connect('users.sqlite3')
CURSOR = CON.cursor()

CURSOR.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER UNIQUE,
username TEXT NOT NULL
)
''')

CON.commit()
CON.close()
