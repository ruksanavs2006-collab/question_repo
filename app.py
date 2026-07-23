from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import sqlite3
import os
import time

app = Flask(__name__)
app.secret_key = "change-this-to-something-random"  # needed for sessions/flash to work

PAPERS_FOLDER = os.path.join(os.path.dirname(__file__), 'papers')
os.makedirs(PAPERS_FOLDER, exist_ok=True)

ADMIN_PASSWORD = "dca2026"  # change this before you submit/demo

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
    connection = get_db_connection()
    # Subjects joined with their course name, so the dropdown reads clearly
    subjects = connection.execute('''
        SELECT subjects.id, subjects.name, subjects.semester, courses.name AS course_name
        FROM subjects
        JOIN courses ON subjects.course_id = courses.id
        ORDER BY courses.name, subjects.semester, subjects.name
    ''').fetchall()
    connection.close()
    return render_template('admin.html', subjects=subjects)


@app.route('/admin/login', methods=['POST'])
def admin_login():
    password = request.form.get('password', '')
    if password == ADMIN_PASSWORD:
        YEARS_BY_COURSE = {
    "B.Sc Computer Applications": [2024, 2025, 2026],
    "B.Voc Software Development": [2025, 2026],
}
        session['is_admin'] = True
        flash("Logged in successfully.")
    else:
        flash("Incorrect password.")
    return redirect(url_for('admin'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin'))


@app.route('/admin/upload', methods=['POST'])
def admin_upload():
     if not session.get('is_admin'):
        return "Not authorized", 403

     subject_id = request.form.get('subject_id', type=int)
     year = request.form.get('year', type=int)
     file = request.files.get('file')

    if not subject_id or not year:
        flash("Please choose a subject and enter a year.")
        return redirect(url_for('admin'))

    connection = get_db_connection()
    subject = connection.execute(
        '''SELECT subjects.id, courses.name AS course_name
           FROM subjects JOIN courses ON subjects.course_id = courses.id
           WHERE subjects.id = ?''',
        (subject_id,)
    ).fetchone()

    if subject is None:
        connection.close()
        flash("Unknown subject.")
        return redirect(url_for('admin'))

    allowed_years = YEARS_BY_COURSE.get(subject['course_name'], [])
    if year not in allowed_years:
        connection.close()
        flash(f"{subject['course_name']} only accepts years: {', '.join(map(str, allowed_years))}.")
        return redirect(url_for('admin'))

    if not file or file.filename == '':
        connection.close()
        flash("Please choose a PDF file.")
        return redirect(url_for('admin'))

    if not file.filename.lower().endswith('.pdf'):
        connection.close()
        flash("Only PDF files are accepted.")
        return redirect(url_for('admin'))

    safe_original = secure_filename(file.filename)
    stored_filename = f"{subject_id}_{year}_{int(time.time())}_{safe_original}"
    file.save(os.path.join(PAPERS_FOLDER, stored_filename))

    connection.execute(
        'INSERT INTO papers (subject_id, year, filename) VALUES (?, ?, ?)',
        (subject_id, year, stored_filename)
    )
    connection.commit()
    connection.close()

    flash("Paper uploaded successfully.")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)