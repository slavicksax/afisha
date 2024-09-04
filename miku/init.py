import sqlite3

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS user_task (
# id INTEGER PRIMARY KEY,
# task TEXT ,
# coord TEXT,
# time_ TEXT,
# history TEXT
# )
# ''')
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS user_name (
# id INTEGER PRIMARY KEY,
# name_ TEXT,
# first_name TEXT
# )
# ''')


coord = '53.894670 27.546987'
query = f"UPDATE user_task SET coord = ? WHERE id = ?;"
cursor.execute(query, (coord, 297843647))
#cursor.execute(f"DROP TABLE IF EXISTS user_name")
connection.commit()
connection.close()