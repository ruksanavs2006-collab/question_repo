import sqlite3

connection = sqlite3.connect('papers.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
)
''')

connection.commit()
connection.close()

print("Database and tables created successfully.")