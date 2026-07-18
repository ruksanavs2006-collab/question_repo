from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os
app = Flask(__name__)
PAPERS_FOLDER = os.path.join(os.path.dirname(__file__), 'papers')

def get_db_connection():
    connection = sqlite3.connect('papers.db')
    connection.row_factory = sqlite3.Row
    return connection

@app.route('/')
def index():
    course_id = request.args.get('course', 1, type=int)

    connection = get_db_connection()
    courses = connection.execute('SELECT * FROM courses').fetchall()
    subjects = connection.execute(
        'SELECT * FROM subjects WHERE course_id = ? ORDER BY semester',
        (course_id,)
    ).fetchall()

    subject_ids = [subject['id'] for subject in subjects]
    papers_by_subject = {}
    if subject_ids:
        placeholders = ','.join('?' for _ in subject_ids)
        papers = connection.execute(
            f'SELECT * FROM papers WHERE subject_id IN ({placeholders}) ORDER BY year DESC',
            subject_ids
        ).fetchall()
        for paper in papers:
            papers_by_subject.setdefault(paper['subject_id'], []).append(paper)

    connection.close()

    subjects_by_semester = {}
    for subject in subjects:
        sem = subject['semester']
        subjects_by_semester.setdefault(sem, []).append(subject)

    return render_template(
        'index.html',
        courses=courses,
        selected_course=course_id,
        subjects_by_semester=subjects_by_semester,
        papers_by_subject=papers_by_subject
    )
@app.route('/download/<int:paper_id>')
def download(paper_id):
    connection = get_db_connection()
    paper = connection.execute('SELECT * FROM papers WHERE id = ?', (paper_id,)).fetchone()
    connection.close()

    if paper is None:
        return "Paper not found", 404

    return send_from_directory(PAPERS_FOLDER, paper['filename'], as_attachment=True)
@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)