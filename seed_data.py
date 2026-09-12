import sqlite3

connection = sqlite3.connect('papers.db')
cursor = connection.cursor()

courses = [
    ('B.Sc Computer Applications',),
    ('B.Voc Software Development',)
]

cursor.executemany('INSERT INTO courses (name) VALUES (?)', courses)

connection.commit()
connection.close()

print("Courses inserted successfully.")
subjects = [
    (1, 1, 'Foundation of Programming and AI'),
    (1, 2, 'Python Programming for Data Science'),
    (1, 3, 'DBMS'),
    (1, 3, 'Principles of Data Science'),
    (1, 3, 'Data Structures in C'),
    (1, 4, 'Advanced Machine Learning Concepts'),
    (1, 4, 'Data Communication and Computer Networks'),
    (1, 4, 'Programming using Java'),
    (1, 5, 'Optimization Techniques'),
    (1, 5, 'Operational Research'),
    (1, 5, 'Software Engineering'),
    (1, 5, 'Cyber Security and Laws'),
    (1, 5, 'Artificial Neural Network')
]

connection = sqlite3.connect('papers.db')
cursor = connection.cursor()

cursor.executemany('INSERT INTO subjects (course_id, semester, name) VALUES (?, ?, ?)', subjects)

connection.commit()
connection.close()

print("Subjects inserted successfully.")