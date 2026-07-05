import os
import re
from datetime import datetime, date
from functools import wraps
from dotenv import load_dotenv

# Load .env file for local development
# On Render, environment variables are set via the dashboard
load_dotenv()

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_from_directory)
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config, allowed_notes_file, allowed_image_file

# ===========================
# App Initialization
# ===========================
app = Flask(__name__)
app.config.from_object(Config)

# ===========================
# MySQL Initialization
# ===========================
mysql = MySQL(app)

# ===========================
# Ensure Upload Folders Exist
# ===========================
os.makedirs(app.config['UPLOAD_NOTES_FOLDER'],  exist_ok=True)
os.makedirs(app.config['UPLOAD_IMAGES_FOLDER'], exist_ok=True)


# ============================================================
# DECORATORS — Login Required Guards
# ============================================================

def student_login_required(f):
    """Decorator: Redirects to login if student is not logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_login_required(f):
    """Decorator: Redirects to admin login if admin is not logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# HOME PAGE
# ============================================================

@app.route('/')
def index():
    """Home page — shows featured courses and platform info."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses LIMIT 6")
    courses = cur.fetchall()
    cur.close()
    return render_template('index.html', courses=courses)


# ============================================================
# AUTHENTICATION — STUDENT
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page."""
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm  = request.form.get('confirm_password', '').strip()

        # Basic validation
        if not all([name, email, phone, password, confirm]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        cur = mysql.connection.cursor()

        # Check if email already exists
        cur.execute("SELECT id FROM students WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing:
            flash('Email already registered. Please login.', 'warning')
            cur.close()
            return redirect(url_for('login'))

        # Hash password and insert student
        hashed_pw = generate_password_hash(password)
        cur.execute(
            "INSERT INTO students (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, hashed_pw)
        )
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Student login page."""
    if 'student_id' in session:
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('login'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE email = %s", (email,))
        student = cur.fetchone()
        cur.close()

        if student and check_password_hash(student['password'], password):
            session['student_id']   = student['id']
            session['student_name'] = student['name']
            flash(f"Welcome back, {student['name']}!", 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Student logout — clears session."""
    session.pop('student_id',   None)
    session.pop('student_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ============================================================
# AUTHENTICATION — ADMIN
# ============================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('admin_login'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cur.fetchone()
        cur.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin_id']       = admin['id']
            session['admin_username'] = admin['username']
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('login.html', admin_mode=True)


@app.route('/admin/logout')
def admin_logout():
    """Admin logout — clears admin session."""
    session.pop('admin_id',       None)
    session.pop('admin_username', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin_login'))


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route('/dashboard')
@student_login_required
def student_dashboard():
    """Student dashboard — shows stats and recent content."""
    student_id = session['student_id']
    cur = mysql.connection.cursor()

    # Fetch student info
    cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()

    # Total courses
    cur.execute("SELECT COUNT(*) AS total FROM courses")
    total_courses = cur.fetchone()['total']

    # Latest 3 videos
    cur.execute("""
        SELECT v.*, c.course_name FROM videos v
        JOIN courses c ON v.course_id = c.id
        ORDER BY v.id DESC LIMIT 3
    """)
    latest_videos = cur.fetchall()

    # Latest 3 notes
    cur.execute("""
        SELECT n.*, c.course_name FROM notes n
        JOIN courses c ON n.course_id = c.id
        ORDER BY n.id DESC LIMIT 3
    """)
    latest_notes = cur.fetchall()

    # Student's quiz results
    cur.execute("""
        SELECT r.*, c.course_name FROM results r
        JOIN courses c ON r.course_id = c.id
        WHERE r.student_id = %s
        ORDER BY r.id DESC LIMIT 5
    """, (student_id,))
    quiz_results = cur.fetchall()

    cur.close()
    return render_template('student_dashboard.html',
                           student=student,
                           total_courses=total_courses,
                           latest_videos=latest_videos,
                           latest_notes=latest_notes,
                           quiz_results=quiz_results)


# ============================================================
# STUDENT PROFILE
# ============================================================

@app.route('/profile', methods=['GET', 'POST'])
@student_login_required
def profile():
    """Student profile — view and update personal info."""
    student_id = session['student_id']
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name or not phone:
            flash('Name and phone are required.', 'danger')
            return redirect(url_for('profile'))

        cur.execute(
            "UPDATE students SET name = %s, phone = %s WHERE id = %s",
            (name, phone, student_id)
        )
        mysql.connection.commit()
        session['student_name'] = name
        flash('Profile updated successfully!', 'success')
        cur.close()
        return redirect(url_for('profile'))

    cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()
    return render_template('profile.html', student=student)


# ============================================================
# COURSES
# ============================================================

@app.route('/courses')
def courses():
    """Courses listing page — viewable by all."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY id DESC")
    all_courses = cur.fetchall()
    cur.close()
    return render_template('courses.html', courses=all_courses)


@app.route('/courses/<int:course_id>')
def course_details(course_id):
    """Individual course detail page with videos, notes, and quiz info."""
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cur.fetchone()

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    cur.execute("SELECT * FROM videos WHERE course_id = %s", (course_id,))
    videos = cur.fetchall()

    cur.execute("SELECT * FROM notes WHERE course_id = %s", (course_id,))
    notes = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS total FROM quiz_questions WHERE course_id = %s", (course_id,))
    quiz_count = cur.fetchone()['total']

    cur.close()
    return render_template('course_details.html',
                           course=course,
                           videos=videos,
                           notes=notes,
                           quiz_count=quiz_count)


# ============================================================
# VIDEOS
# ============================================================

@app.route('/videos')
def videos():
    """Videos listing page with course filter."""
    course_id = request.args.get('course_id', '')
    search    = request.args.get('search', '').strip()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY course_name")
    all_courses = cur.fetchall()

    query  = "SELECT v.*, c.course_name FROM videos v JOIN courses c ON v.course_id = c.id WHERE 1=1"
    params = []

    if course_id:
        query += " AND v.course_id = %s"
        params.append(course_id)

    if search:
        query += " AND v.title LIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY v.id DESC"
    cur.execute(query, params)
    all_videos = cur.fetchall()
    cur.close()

    return render_template('videos.html',
                           videos=all_videos,
                           courses=all_courses,
                           selected_course=course_id,
                           search=search)


# ============================================================
# NOTES
# ============================================================

@app.route('/notes')
def notes():
    """Notes listing page with course filter and search."""
    course_id = request.args.get('course_id', '')
    search    = request.args.get('search', '').strip()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY course_name")
    all_courses = cur.fetchall()

    query  = "SELECT n.*, c.course_name FROM notes n JOIN courses c ON n.course_id = c.id WHERE 1=1"
    params = []

    if course_id:
        query += " AND n.course_id = %s"
        params.append(course_id)

    if search:
        query += " AND n.title LIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY n.id DESC"
    cur.execute(query, params)
    all_notes = cur.fetchall()
    cur.close()

    return render_template('notes.html',
                           notes=all_notes,
                           courses=all_courses,
                           selected_course=course_id,
                           search=search)


@app.route('/notes/download/<int:note_id>')
@student_login_required
def download_note(note_id):
    """Download a PDF note — students only."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
    note = cur.fetchone()
    cur.close()

    if not note:
        flash('Note not found.', 'danger')
        return redirect(url_for('notes'))

    return send_from_directory(
        app.config['UPLOAD_NOTES_FOLDER'],
        note['pdf_file'],
        as_attachment=True
    )


# ============================================================
# QUIZ
# ============================================================

@app.route('/quiz/<int:course_id>', methods=['GET', 'POST'])
@student_login_required
def quiz(course_id):
    """Quiz page — loads MCQ questions for a course."""
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cur.fetchone()

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    cur.execute("SELECT * FROM quiz_questions WHERE course_id = %s", (course_id,))
    questions = cur.fetchall()
    cur.close()

    if not questions:
        flash('No quiz questions available for this course yet.', 'info')
        return redirect(url_for('course_details', course_id=course_id))

    if request.method == 'POST':
        score   = 0
        results = []

        for question in questions:
            q_id            = str(question['id'])
            selected_answer = request.form.get(f'question_{q_id}', '').strip()
            correct_answer  = question['answer'].strip()
            is_correct      = (selected_answer == correct_answer)

            if is_correct:
                score += 1

            results.append({
                'question':        question['question'],
                'selected_answer': selected_answer,
                'correct_answer':  correct_answer,
                'is_correct':      is_correct,
                'option1':         question['option1'],
                'option2':         question['option2'],
                'option3':         question['option3'],
                'option4':         question['option4'],
            })

        total      = len(questions)
        percentage = round((score / total) * 100, 2) if total > 0 else 0

        # Save result to database
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO results (student_id, course_id, score) VALUES (%s, %s, %s)",
            (session['student_id'], course_id, score)
        )
        mysql.connection.commit()
        cur.close()

        return render_template('result.html',
                               course=course,
                               score=score,
                               total=total,
                               percentage=percentage,
                               results=results)

    return render_template('quiz.html', course=course, questions=questions)


# ============================================================
# FEEDBACK
# ============================================================

@app.route('/feedback', methods=['GET', 'POST'])
@student_login_required
def feedback():
    """Feedback submission page for students."""
    if request.method == 'POST':
        message = request.form.get('message', '').strip()

        if not message:
            flash('Feedback message cannot be empty.', 'danger')
            return redirect(url_for('feedback'))

        if len(message) < 10:
            flash('Please write a more detailed feedback (at least 10 characters).', 'warning')
            return redirect(url_for('feedback'))

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO feedback (student_id, message, date) VALUES (%s, %s, %s)",
            (session['student_id'], message, date.today())
        )
        mysql.connection.commit()
        cur.close()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('feedback.html')


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    """Admin dashboard — overview of all platform data."""
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM courses")
    total_courses = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM videos")
    total_videos = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM notes")
    total_notes = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM quiz_questions")
    total_questions = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM results")
    total_results = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM feedback")
    total_feedback = cur.fetchone()['total']

    # Recent students
    cur.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5")
    recent_students = cur.fetchall()

    # Recent feedback
    cur.execute("""
        SELECT f.*, s.name AS student_name FROM feedback f
        JOIN students s ON f.student_id = s.id
        ORDER BY f.id DESC LIMIT 5
    """)
    recent_feedback = cur.fetchall()

    cur.close()
    return render_template('admin_dashboard.html',
                           total_students=total_students,
                           total_courses=total_courses,
                           total_videos=total_videos,
                           total_notes=total_notes,
                           total_questions=total_questions,
                           total_results=total_results,
                           total_feedback=total_feedback,
                           recent_students=recent_students,
                           recent_feedback=recent_feedback)


# ============================================================
# ADMIN — COURSE MANAGEMENT
# ============================================================

@app.route('/admin/courses')
@admin_login_required
def admin_courses():
    """Admin: View all courses."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY id DESC")
    all_courses = cur.fetchall()
    cur.close()
    return render_template('admin_dashboard.html',
                           section='courses',
                           courses=all_courses)


@app.route('/admin/courses/add', methods=['GET', 'POST'])
@admin_login_required
def admin_add_course():
    """Admin: Add a new course."""
    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        description = request.form.get('description', '').strip()
        image_file  = request.files.get('image')
        image_name  = 'default_course.jpg'

        if not course_name or not description:
            flash('Course name and description are required.', 'danger')
            return redirect(url_for('admin_add_course'))

        # Handle image upload
        if image_file and image_file.filename != '':
            if allowed_image_file(image_file.filename):
                filename   = secure_filename(image_file.filename)
                image_name = f"course_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                image_file.save(os.path.join(app.config['UPLOAD_IMAGES_FOLDER'], image_name))
            else:
                flash('Invalid image format. Use PNG, JPG, JPEG, GIF, or WEBP.', 'danger')
                return redirect(url_for('admin_add_course'))

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO courses (course_name, description, image) VALUES (%s, %s, %s)",
            (course_name, description, image_name)
        )
        mysql.connection.commit()
        cur.close()

        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', section='add_course')


@app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_login_required
def admin_edit_course(course_id):
    """Admin: Edit an existing course."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cur.fetchone()

    if not course:
        flash('Course not found.', 'danger')
        cur.close()
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        description = request.form.get('description', '').strip()
        image_file  = request.files.get('image')
        image_name  = course['image']

        if not course_name or not description:
            flash('Course name and description are required.', 'danger')
            return redirect(url_for('admin_edit_course', course_id=course_id))

        if image_file and image_file.filename != '':
            if allowed_image_file(image_file.filename):
                filename   = secure_filename(image_file.filename)
                image_name = f"course_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                image_file.save(os.path.join(app.config['UPLOAD_IMAGES_FOLDER'], image_name))
            else:
                flash('Invalid image format.', 'danger')
                return redirect(url_for('admin_edit_course', course_id=course_id))

        cur.execute(
            "UPDATE courses SET course_name=%s, description=%s, image=%s WHERE id=%s",
            (course_name, description, image_name, course_id)
        )
        mysql.connection.commit()
        cur.close()

        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cur.close()
    return render_template('admin_dashboard.html', section='edit_course', course=course)


@app.route('/admin/courses/delete/<int:course_id>')
@admin_login_required
def admin_delete_course(course_id):
    """Admin: Delete a course and its related content."""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM videos WHERE course_id = %s",        (course_id,))
    cur.execute("DELETE FROM notes WHERE course_id = %s",         (course_id,))
    cur.execute("DELETE FROM quiz_questions WHERE course_id = %s", (course_id,))
    cur.execute("DELETE FROM results WHERE course_id = %s",       (course_id,))
    cur.execute("DELETE FROM courses WHERE id = %s",              (course_id,))
    mysql.connection.commit()
    cur.close()

    flash('Course and all related content deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================================
# ADMIN — VIDEO MANAGEMENT
# ============================================================

@app.route('/admin/videos/add', methods=['GET', 'POST'])
@admin_login_required
def admin_add_video():
    """Admin: Add a YouTube video link to a course."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY course_name")
    all_courses = cur.fetchall()

    if request.method == 'POST':
        title        = request.form.get('title', '').strip()
        course_id    = request.form.get('course_id', '').strip()
        youtube_link = request.form.get('youtube_link', '').strip()

        if not all([title, course_id, youtube_link]):
            flash('All fields are required.', 'danger')
            return render_template('admin_dashboard.html',
                                   section='add_video', courses=all_courses)

        # Convert YouTube watch URL to embed URL if needed
        if 'watch?v=' in youtube_link:
            youtube_link = youtube_link.replace('watch?v=', 'embed/')
        elif 'youtu.be/' in youtube_link:
            video_id     = youtube_link.split('youtu.be/')[-1].split('?')[0]
            youtube_link = f"https://www.youtube.com/embed/{video_id}"

        cur.execute(
            "INSERT INTO videos (title, course_id, youtube_link) VALUES (%s, %s, %s)",
            (title, course_id, youtube_link)
        )
        mysql.connection.commit()
        cur.close()

        flash('Video added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cur.close()
    return render_template('admin_dashboard.html',
                           section='add_video', courses=all_courses)


@app.route('/admin/videos/delete/<int:video_id>')
@admin_login_required
def admin_delete_video(video_id):
    """Admin: Delete a video."""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM videos WHERE id = %s", (video_id,))
    mysql.connection.commit()
    cur.close()
    flash('Video deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================================
# ADMIN — NOTES MANAGEMENT
# ============================================================

@app.route('/admin/notes/add', methods=['GET', 'POST'])
@admin_login_required
def admin_add_note():
    """Admin: Upload a PDF note for a course."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY course_name")
    all_courses = cur.fetchall()

    if request.method == 'POST':
        title     = request.form.get('title', '').strip()
        course_id = request.form.get('course_id', '').strip()
        pdf_file  = request.files.get('pdf_file')

        if not title or not course_id or not pdf_file or pdf_file.filename == '':
            flash('All fields including PDF file are required.', 'danger')
            return render_template('admin_dashboard.html',
                                   section='add_note', courses=all_courses)

        if not allowed_notes_file(pdf_file.filename):
            flash('Only PDF files are allowed.', 'danger')
            return render_template('admin_dashboard.html',
                                   section='add_note', courses=all_courses)

        filename  = secure_filename(pdf_file.filename)
        pdf_name  = f"note_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        pdf_file.save(os.path.join(app.config['UPLOAD_NOTES_FOLDER'], pdf_name))

        cur.execute(
            "INSERT INTO notes (title, course_id, pdf_file) VALUES (%s, %s, %s)",
            (title, course_id, pdf_name)
        )
        mysql.connection.commit()
        cur.close()

        flash('Note uploaded successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cur.close()
    return render_template('admin_dashboard.html',
                           section='add_note', courses=all_courses)


@app.route('/admin/notes/delete/<int:note_id>')
@admin_login_required
def admin_delete_note(note_id):
    """Admin: Delete a note and its PDF file."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
    note = cur.fetchone()

    if note:
        # Delete the physical file
        file_path = os.path.join(app.config['UPLOAD_NOTES_FOLDER'], note['pdf_file'])
        if os.path.exists(file_path):
            os.remove(file_path)

        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        mysql.connection.commit()

    cur.close()
    flash('Note deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================================
# ADMIN — QUIZ MANAGEMENT
# ============================================================

@app.route('/admin/quiz/add', methods=['GET', 'POST'])
@admin_login_required
def admin_add_quiz():
    """Admin: Add a quiz question to a course."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY course_name")
    all_courses = cur.fetchall()

    if request.method == 'POST':
        course_id = request.form.get('course_id', '').strip()
        question  = request.form.get('question', '').strip()
        option1   = request.form.get('option1', '').strip()
        option2   = request.form.get('option2', '').strip()
        option3   = request.form.get('option3', '').strip()
        option4   = request.form.get('option4', '').strip()
        answer    = request.form.get('answer', '').strip()

        if not all([course_id, question, option1, option2, option3, option4, answer]):
            flash('All fields are required.', 'danger')
            return render_template('admin_dashboard.html',
                                   section='add_quiz', courses=all_courses)

        if answer not in [option1, option2, option3, option4]:
            flash('The correct answer must match one of the four options exactly.', 'danger')
            return render_template('admin_dashboard.html',
                                   section='add_quiz', courses=all_courses)

        cur.execute("""
            INSERT INTO quiz_questions
            (course_id, question, option1, option2, option3, option4, answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (course_id, question, option1, option2, option3, option4, answer))
        mysql.connection.commit()
        cur.close()

        flash('Quiz question added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cur.close()
    return render_template('admin_dashboard.html',
                           section='add_quiz', courses=all_courses)


@app.route('/admin/quiz/delete/<int:question_id>')
@admin_login_required
def admin_delete_quiz(question_id):
    """Admin: Delete a quiz question."""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM quiz_questions WHERE id = %s", (question_id,))
    mysql.connection.commit()
    cur.close()
    flash('Quiz question deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


# ============================================================
# ADMIN — STUDENTS, RESULTS, FEEDBACK VIEWS
# ============================================================

@app.route('/admin/students')
@admin_login_required
def admin_students():
    """Admin: View all registered students."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    all_students = cur.fetchall()
    cur.close()
    return render_template('admin_dashboard.html',
                           section='students', students=all_students)


@app.route('/admin/students/delete/<int:student_id>')
@admin_login_required
def admin_delete_student(student_id):
    """Admin: Delete a student account."""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM feedback WHERE student_id = %s", (student_id,))
    cur.execute("DELETE FROM results WHERE student_id = %s",  (student_id,))
    cur.execute("DELETE FROM students WHERE id = %s",         (student_id,))
    mysql.connection.commit()
    cur.close()
    flash('Student deleted.', 'success')
    return redirect(url_for('admin_students'))


@app.route('/admin/results')
@admin_login_required
def admin_results():
    """Admin: View all quiz results."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.*, s.name AS student_name, c.course_name
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN courses c  ON r.course_id  = c.id
        ORDER BY r.id DESC
    """)
    all_results = cur.fetchall()
    cur.close()
    return render_template('admin_dashboard.html',
                           section='results', results=all_results)


@app.route('/admin/feedback')
@admin_login_required
def admin_feedback():
    """Admin: View all student feedback."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.*, s.name AS student_name
        FROM feedback f
        JOIN students s ON f.student_id = s.id
        ORDER BY f.id DESC
    """)
    all_feedback = cur.fetchall()
    cur.close()
    return render_template('admin_dashboard.html',
                           section='feedback', feedback=all_feedback)


# ============================================================
# ADMIN — MANAGE ALL IN ONE VIEW
# ============================================================

@app.route('/admin/manage/<string:section>')
@admin_login_required
def admin_manage(section):
    """Admin: Dynamic section loader for manage pages."""
    cur = mysql.connection.cursor()
    data = {}

    if section == 'videos':
        cur.execute("""
            SELECT v.*, c.course_name FROM videos v
            JOIN courses c ON v.course_id = c.id
            ORDER BY v.id DESC
        """)
        data['videos'] = cur.fetchall()

    elif section == 'notes':
        cur.execute("""
            SELECT n.*, c.course_name FROM notes n
            JOIN courses c ON n.course_id = c.id
            ORDER BY n.id DESC
        """)
        data['notes'] = cur.fetchall()

    elif section == 'quiz':
        cur.execute("""
            SELECT q.*, c.course_name FROM quiz_questions q
            JOIN courses c ON q.course_id = c.id
            ORDER BY q.id DESC
        """)
        data['questions'] = cur.fetchall()

    elif section == 'courses':
        cur.execute("SELECT * FROM courses ORDER BY id DESC")
        data['courses'] = cur.fetchall()

    cur.close()
    return render_template('admin_dashboard.html', section=section, **data)


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(413)
def file_too_large(e):
    flash('File is too large. Maximum allowed size is 16 MB.', 'danger')
    return redirect(request.referrer or url_for('index'))


@app.errorhandler(500)
def internal_error(e):
    flash('An internal server error occurred. Please try again.', 'danger')
    return redirect(url_for('index'))


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
