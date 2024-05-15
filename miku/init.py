import sqlite3

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_task (
id INTEGER PRIMARY KEY,
task TEXT ,
coord TEXT,
time_ TEXT,
history TEXT
)
''')


cursor.execute(f"DROP TABLE IF EXISTS giggles_task")
connection.commit()
connection.close()