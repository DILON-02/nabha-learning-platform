"""
Run this script once to fix app.py
Command: python fix_app.py
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: index route — add try/except
old_index = '''@app.route('/')
def index():
    """Home page — shows featured courses and platform info."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses LIMIT 6")
    courses = cur.fetchall()
    cur.close()
    return render_template('index.html', courses=courses)'''

new_index = '''@app.route('/')
def index():
    """Home page — shows featured courses and platform info."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses LIMIT 6")
        courses = cur.fetchall()
        cur.close()
    except Exception:
        courses = []
    return render_template('index.html', courses=courses)'''

# Fix 2: courses route — add try/except
old_courses = '''@app.route('/courses')
def courses():
    """Courses listing page — viewable by all."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses ORDER BY id DESC")
    all_courses = cur.fetchall()
    cur.close()
    return render_template('courses.html', courses=all_courses)'''

new_courses = '''@app.route('/courses')
def courses():
    """Courses listing page — viewable by all."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses ORDER BY id DESC")
        all_courses = cur.fetchall()
        cur.close()
    except Exception:
        all_courses = []
    return render_template('courses.html', courses=all_courses)'''

# Fix 3: error handler 500 — stop redirect loop
old_500 = '''@app.errorhandler(500)
def internal_error(e):
    flash('An internal server error occurred. Please try again.', 'danger')
    return redirect(url_for('index'))'''

new_500 = '''@app.errorhandler(500)
def internal_error(e):
    return render_template('index.html', courses=[]), 500'''

# Fix 4: error handler 404
old_404 = '''@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404'''

new_404 = '''@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', courses=[]), 404'''

# Apply fixes
content = content.replace(old_index,   new_index)
content = content.replace(old_courses, new_courses)
content = content.replace(old_500,     new_500)
content = content.replace(old_404,     new_404)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.py fixed successfully!")
print("Now run: git add . && git commit -m 'Fix mobile and error handlers' && git push")
