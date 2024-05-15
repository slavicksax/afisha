import sqlite3

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS user_task (
id INTEGER PRIMARY KEY,
task TEXT CHECK(task IN ('RESTORAN', 'PUB', 'NONE','BACK_PUB','BACK_REST','ADD_REST','ADD_PUB','SD3')),
text TEXT
)
''')


sql = "INSERT INTO Users (id) VALUES (?)"
values = (111,)
#cursor.execute(sql, values)


connection.commit()


connection.close()