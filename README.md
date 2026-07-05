# 📚 Digital Learning Platform for Rural School Students — Nabha

A complete, production-ready web application built with **Python Flask**, **MySQL**, **Bootstrap 5**, and **JavaScript** to provide free quality digital education to rural school students in Nabha, Punjab.

---

## 🎯 Project Overview

The **Digital Learning Platform (DLP) Nabha** is a full-stack web application that bridges the digital education gap for rural school students. It provides a centralized platform where students can access video lessons, download study notes, take MCQ quizzes, and track their learning progress — completely free of charge.

This project was developed as a **Third-Year B.E. Major Project** using modern web technologies and follows industry best practices for code quality, security, and deployment.

---

## ✨ Features

### 👨‍🎓 Student Features
- ✅ Register and Login securely
- ✅ Personal Dashboard with learning overview
- ✅ Browse and view all available courses
- ✅ Watch embedded YouTube video lessons
- ✅ Download PDF study notes
- ✅ Take MCQ quizzes with automatic evaluation
- ✅ View detailed quiz results with correct answers
- ✅ Track learning progress and quiz scores
- ✅ Update personal profile (name, phone)
- ✅ Submit platform feedback

### 🔐 Admin Features
- ✅ Secure admin login panel
- ✅ Dashboard with platform statistics
- ✅ Add, Edit, Delete courses
- ✅ Upload YouTube video links per course
- ✅ Upload PDF notes per course
- ✅ Create and delete MCQ quiz questions
- ✅ View and manage all registered students
- ✅ View all quiz results
- ✅ Read all student feedback

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, JavaScript (ES6) |
| **Backend** | Python 3.x, Flask 3.0 |
| **Database** | MySQL 8.0 |
| **ORM / DB Driver** | Flask-MySQLdb, mysqlclient |
| **Security** | Werkzeug password hashing, Flask sessions |
| **Icons** | Font Awesome 6.5 |
| **Fonts** | Google Fonts (Inter) |
| **Deployment** | Render (gunicorn) |
| **Version Control** | Git, GitHub |

---

## 📁 Folder Structure

```
Digital-Learning-Platform/
│
├── static/
│   ├── css/
│   │   └── style.css              # Complete custom stylesheet
│   ├── js/
│   │   └── script.js              # All interactive JavaScript
│   └── images/
│       └── uploads/
│           ├── notes/             # Uploaded PDF notes
│           └── course_images/     # Uploaded course images
│
├── templates/
│   ├── base.html                  # Master layout template
│   ├── index.html                 # Home page
│   ├── login.html                 # Student & admin login
│   ├── register.html              # Student registration
│   ├── student_dashboard.html     # Student dashboard
│   ├── admin_dashboard.html       # Admin panel (all sections)
│   ├── courses.html               # Course listing
│   ├── course_details.html        # Individual course page
│   ├── videos.html                # Video lessons listing
│   ├── notes.html                 # Notes listing & download
│   ├── quiz.html                  # Interactive MCQ quiz
│   ├── result.html                # Quiz result page
│   ├── profile.html               # Student profile
│   └── feedback.html              # Feedback form
│
├── database/
│   └── learning.sql               # Complete DB schema + sample data
│
├── app.py                         # Main Flask application
├── config.py                      # Configuration (DB, uploads, keys)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Git

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/Digital-Learning-Platform.git
cd Digital-Learning-Platform
```

---

### Step 2 — Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up MySQL Database

```bash
# Open MySQL
mysql -u root -p

# Import the database
source /path/to/Digital-Learning-Platform/database/learning.sql
```

Or import directly from terminal:

```bash
mysql -u root -p < database/learning.sql
```

---

### Step 5 — Set Up Admin Password

After importing the database, set a proper hashed admin password:

```bash
# Generate hash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"
```

Copy the output hash, then run in MySQL:

```sql
USE learning_platform;
UPDATE admin SET password='<paste_hash_here>' WHERE username='admin';
```

---

### Step 6 — Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_very_strong_secret_key_here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=learning_platform
```

---

### Step 7 — Create Upload Folders

```bash
mkdir -p static/images/uploads/notes
mkdir -p static/images/uploads/course_images
```

---

### Step 8 — Run the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🔑 Default Login Credentials

### Admin Login
- **URL:** http://localhost:5000/admin/login
- **Username:** `admin`
- **Password:** `admin123` (after Step 5 above)

### Student Login
Register at: http://localhost:5000/register

---

## 🗄️ Database Schema

| Table | Description |
|---|---|
| `admin` | Admin login credentials |
| `students` | Registered student accounts |
| `courses` | Course information and images |
| `videos` | YouTube video links per course |
| `notes` | Uploaded PDF notes per course |
| `quiz_questions` | MCQ questions with options and answer |
| `results` | Student quiz scores |
| `feedback` | Student feedback messages |

---

## 📸 Screenshots

> _Add screenshots of the following pages after setup:_

| Page | Screenshot |
|---|---|
| Home Page | `screenshots/home.png` |
| Student Dashboard | `screenshots/student_dashboard.png` |
| Admin Dashboard | `screenshots/admin_dashboard.png` |
| Courses Page | `screenshots/courses.png` |
| Quiz Page | `screenshots/quiz.png` |
| Result Page | `screenshots/result.png` |

---

## 🚀 Deployment on Render

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit — Digital Learning Platform Nabha"
git remote add origin https://github.com/yourusername/Digital-Learning-Platform.git
git push -u origin main
```

### Step 2 — Create Web Service on Render
1. Go to [https://render.com](https://render.com) and sign up
2. Click **New → Web Service**
3. Connect your GitHub repository
4. Set **Build Command:** `pip install -r requirements.txt`
5. Set **Start Command:** `gunicorn app:app`

### Step 3 — Add Environment Variables on Render
In Render dashboard → Environment → Add:
```
SECRET_KEY        = your_secret_key
MYSQL_HOST        = your_render_mysql_host
MYSQL_USER        = your_db_user
MYSQL_PASSWORD    = your_db_password
MYSQL_DB          = learning_platform
```

### Step 4 — Add MySQL Database on Render
1. Click **New → PostgreSQL** (or use external MySQL provider like **PlanetScale** or **Railway**)
2. Connect credentials to environment variables above

---

## 🧪 Testing Guide

### Manual Test Checklist

#### Student Flow
- [ ] Register a new student account
- [ ] Login with registered credentials
- [ ] View student dashboard
- [ ] Browse all courses
- [ ] View course details
- [ ] Watch an embedded video
- [ ] Download a PDF note (login required)
- [ ] Take a quiz and submit
- [ ] View quiz results with correct answers
- [ ] Update profile (name, phone)
- [ ] Submit feedback
- [ ] Logout

#### Admin Flow
- [ ] Login to admin panel at `/admin/login`
- [ ] View dashboard statistics
- [ ] Add a new course with image
- [ ] Edit an existing course
- [ ] Delete a course
- [ ] Add a YouTube video link
- [ ] Upload a PDF note
- [ ] Add MCQ quiz questions
- [ ] View all registered students
- [ ] View all quiz results
- [ ] Read student feedback
- [ ] Logout

---

## 🔮 Future Scope

- [ ] Email verification on registration
- [ ] Password reset via email (Flask-Mail)
- [ ] Course enrollment tracking
- [ ] Certificate generation on quiz completion
- [ ] Video progress tracking
- [ ] Multiple admin accounts with role management
- [ ] Student leaderboard
- [ ] Multi-language support (Hindi, Punjabi)
- [ ] Mobile app (Flutter/React Native)
- [ ] SMS notifications (Twilio)
- [ ] Offline mode with service workers (PWA)

---

## 👨‍💻 Author

**Project:** Digital Learning Platform for Rural School Students — Nabha
**Developed By:** [Your Name]
**College:** [Your College Name]
**Department:** [Your Department]
**Year:** Third Year B.E. — Major Project
**Session:** 2024–2025

---

## 📄 License

This project is developed for educational purposes as a college major project.
Feel free to use, modify, and distribute with attribution.

---

## 🙏 Acknowledgements

- **Bootstrap** — Responsive UI framework
- **Font Awesome** — Icon library
- **Flask** — Python web framework
- **Werkzeug** — Password hashing and security utilities
- **Google Fonts** — Inter typeface

---

> _Built with ❤️ to empower rural students in Nabha, Punjab, India._
