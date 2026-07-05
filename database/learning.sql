-- ============================================================
-- DIGITAL LEARNING PLATFORM FOR RURAL SCHOOL STUDENTS - NABHA
-- Database: learning_platform
-- ============================================================

-- Create and select the database
CREATE DATABASE IF NOT EXISTS learning_platform
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE learning_platform;

-- ============================================================
-- TABLE: admin
-- Stores admin login credentials
-- ============================================================
CREATE TABLE IF NOT EXISTS admin (
    id       INT          NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: students
-- Stores registered student information
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id       INT          NOT NULL AUTO_INCREMENT,
    name     VARCHAR(150) NOT NULL,
    email    VARCHAR(150) NOT NULL UNIQUE,
    phone    VARCHAR(15)  NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: courses
-- Stores course information
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    id          INT          NOT NULL AUTO_INCREMENT,
    course_name VARCHAR(200) NOT NULL,
    description TEXT         NOT NULL,
    image       VARCHAR(255) NOT NULL DEFAULT 'default_course.jpg',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: videos
-- Stores YouTube video links linked to courses
-- ============================================================
CREATE TABLE IF NOT EXISTS videos (
    id           INT          NOT NULL AUTO_INCREMENT,
    title        VARCHAR(255) NOT NULL,
    course_id    INT          NOT NULL,
    youtube_link VARCHAR(500) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_video_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: notes
-- Stores uploaded PDF notes linked to courses
-- ============================================================
CREATE TABLE IF NOT EXISTS notes (
    id        INT          NOT NULL AUTO_INCREMENT,
    title     VARCHAR(255) NOT NULL,
    course_id INT          NOT NULL,
    pdf_file  VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_note_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: quiz_questions
-- Stores MCQ questions with options and correct answer
-- ============================================================
CREATE TABLE IF NOT EXISTS quiz_questions (
    id        INT          NOT NULL AUTO_INCREMENT,
    course_id INT          NOT NULL,
    question  TEXT         NOT NULL,
    option1   VARCHAR(255) NOT NULL,
    option2   VARCHAR(255) NOT NULL,
    option3   VARCHAR(255) NOT NULL,
    option4   VARCHAR(255) NOT NULL,
    answer    VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_quiz_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: results
-- Stores student quiz results
-- ============================================================
CREATE TABLE IF NOT EXISTS results (
    id         INT NOT NULL AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id  INT NOT NULL,
    score      INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    CONSTRAINT fk_result_student
        FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_result_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: feedback
-- Stores student feedback messages
-- ============================================================
CREATE TABLE IF NOT EXISTS feedback (
    id         INT  NOT NULL AUTO_INCREMENT,
    student_id INT  NOT NULL,
    message    TEXT NOT NULL,
    date       DATE NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_feedback_student
        FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ============================================================
-- SAMPLE DATA
-- ============================================================

-- ============================================================
-- Admin Account
-- Password: admin123
-- (hashed with werkzeug generate_password_hash)
-- ============================================================
INSERT INTO admin (username, password) VALUES
(
    'admin',
    'scrypt:32768:8:1$abc123salt$hashedpasswordplaceholder'
);

-- NOTE: Run this Python snippet once to get the real hash:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('admin123'))
-- Then replace the hash above with the output.

-- For convenience, use this route after setup to reset admin password:
-- UPDATE admin SET password='<new_hash>' WHERE username='admin';


-- ============================================================
-- Sample Courses
-- ============================================================
INSERT INTO courses (course_name, description, image) VALUES
(
    'Mathematics - Class 9',
    'Complete Class 9 Mathematics covering Number Systems, Polynomials, Coordinate Geometry, Linear Equations, Triangles, Circles, Heron Formula, Surface Area, Volume and Statistics.',
    'default_course.jpg'
),
(
    'Science - Class 9',
    'Class 9 Science covering Matter in Our Surroundings, Atoms and Molecules, Cell Biology, Motion, Force and Laws of Motion, Gravitation, Sound and Natural Resources.',
    'default_course.jpg'
),
(
    'English Grammar',
    'English Grammar fundamentals including Tenses, Articles, Prepositions, Conjunctions, Voice, Narration, Comprehension and Essay Writing for school students.',
    'default_course.jpg'
),
(
    'Social Science - Class 9',
    'Social Science covering History (French Revolution, Russian Revolution, Nazism), Geography (India Size and Location, Drainage, Climate), Political Science and Economics.',
    'default_course.jpg'
),
(
    'Computer Science Basics',
    'Introduction to Computer Science including hardware, software, operating systems, MS Office, internet basics, programming concepts and cyber safety.',
    'default_course.jpg'
),
(
    'Hindi - Class 9',
    'Hindi language course covering Kshitij, Kritika, Sparsh prose and poetry with grammar, comprehension, writing skills and literature analysis.',
    'default_course.jpg'
);


-- ============================================================
-- Sample Videos (YouTube embed links)
-- ============================================================
INSERT INTO videos (title, course_id, youtube_link) VALUES
('Introduction to Number Systems',          1, 'https://www.youtube.com/embed/RqpNQJoGCGk'),
('Polynomials - Class 9 Complete Chapter',  1, 'https://www.youtube.com/embed/hW5DKA-0GuY'),
('Coordinate Geometry Explained',           1, 'https://www.youtube.com/embed/RWF8mZFf_1w'),
('Matter in Our Surroundings',              2, 'https://www.youtube.com/embed/5bz7SykCKDE'),
('Atoms and Molecules Full Chapter',        2, 'https://www.youtube.com/embed/uIBVz2FFgHo'),
('Cell Structure and Function',             2, 'https://www.youtube.com/embed/URUJD5NEXC8'),
('English Tenses Complete Guide',           3, 'https://www.youtube.com/embed/5bz7SykCKDE'),
('Articles A An The - Rules and Examples',  3, 'https://www.youtube.com/embed/RqpNQJoGCGk'),
('French Revolution - Class 9 History',     4, 'https://www.youtube.com/embed/hW5DKA-0GuY'),
('India Size and Location - Geography',     4, 'https://www.youtube.com/embed/RWF8mZFf_1w'),
('Computer Hardware and Software Basics',   5, 'https://www.youtube.com/embed/uIBVz2FFgHo'),
('Introduction to Internet and Browsers',   5, 'https://www.youtube.com/embed/URUJD5NEXC8');


-- ============================================================
-- Sample Quiz Questions — Mathematics
-- ============================================================
INSERT INTO quiz_questions (course_id, question, option1, option2, option3, option4, answer) VALUES
(
    1,
    'Which of the following is an irrational number?',
    '√4', '√9', '√2', '√16',
    '√2'
),
(
    1,
    'The degree of the polynomial 3x³ + 2x² - x + 5 is:',
    '1', '2', '3', '5',
    '3'
),
(
    1,
    'The point (0, 0) in coordinate geometry is called:',
    'X-axis', 'Y-axis', 'Origin', 'Quadrant',
    'Origin'
),
(
    1,
    'If x + y = 10 and x = 4, what is y?',
    '4', '6', '10', '14',
    '6'
),
(
    1,
    'The sum of angles in a triangle is:',
    '90°', '180°', '270°', '360°',
    '180°'
);

-- ============================================================
-- Sample Quiz Questions — Science
-- ============================================================
INSERT INTO quiz_questions (course_id, question, option1, option2, option3, option4, answer) VALUES
(
    2,
    'What is the SI unit of force?',
    'Watt', 'Joule', 'Newton', 'Pascal',
    'Newton'
),
(
    2,
    'Which organelle is known as the powerhouse of the cell?',
    'Nucleus', 'Mitochondria', 'Ribosome', 'Chloroplast',
    'Mitochondria'
),
(
    2,
    'The chemical formula of water is:',
    'H2O2', 'HO', 'H2O', 'H3O',
    'H2O'
),
(
    2,
    'Sound cannot travel through:',
    'Water', 'Air', 'Steel', 'Vacuum',
    'Vacuum'
),
(
    2,
    'Which law states that every action has an equal and opposite reaction?',
    'Newton First Law', 'Newton Second Law', 'Newton Third Law', 'Law of Gravitation',
    'Newton Third Law'
);

-- ============================================================
-- Sample Quiz Questions — English Grammar
-- ============================================================
INSERT INTO quiz_questions (course_id, question, option1, option2, option3, option4, answer) VALUES
(
    3,
    'Choose the correct article: ___ apple a day keeps the doctor away.',
    'A', 'An', 'The', 'No article',
    'An'
),
(
    3,
    'She ___ to school every day. (Simple Present)',
    'go', 'goes', 'went', 'going',
    'goes'
),
(
    3,
    'The plural of "child" is:',
    'Childs', 'Childes', 'Children', 'Childrens',
    'Children'
),
(
    3,
    'Which sentence is in passive voice?',
    'She writes a letter', 'A letter is written by her', 'She wrote a letter', 'She will write a letter',
    'A letter is written by her'
),
(
    3,
    'The synonym of "happy" is:',
    'Sad', 'Angry', 'Joyful', 'Tired',
    'Joyful'
);

-- ============================================================
-- Sample Quiz Questions — Computer Science
-- ============================================================
INSERT INTO quiz_questions (course_id, question, option1, option2, option3, option4, answer) VALUES
(
    5,
    'CPU stands for:',
    'Central Processing Unit', 'Computer Processing Unit', 'Central Program Unit', 'Core Processing Unit',
    'Central Processing Unit'
),
(
    5,
    'Which of the following is an input device?',
    'Monitor', 'Printer', 'Keyboard', 'Speaker',
    'Keyboard'
),
(
    5,
    'The full form of WWW is:',
    'World Wide Web', 'World Web Wide', 'Wide World Web', 'Web World Wide',
    'World Wide Web'
),
(
    5,
    'Which is NOT an operating system?',
    'Windows', 'Linux', 'Android', 'MS Word',
    'MS Word'
),
(
    5,
    'RAM stands for:',
    'Read Access Memory', 'Random Access Memory', 'Rapid Access Memory', 'Read And Memory',
    'Random Access Memory'
);


-- ============================================================
-- Sample Students
-- Password for all sample students: student123
-- ============================================================
INSERT INTO students (name, email, phone, password) VALUES
(
    'Rahul Sharma',
    'rahul@example.com',
    '9876543210',
    'scrypt:32768:8:1$placeholder$hashedpassword1'
),
(
    'Priya Kumari',
    'priya@example.com',
    '9876543211',
    'scrypt:32768:8:1$placeholder$hashedpassword2'
),
(
    'Amit Singh',
    'amit@example.com',
    '9876543212',
    'scrypt:32768:8:1$placeholder$hashedpassword3'
);

-- NOTE: Sample student passwords above are placeholder hashes.
-- Students should register through the /register page to get proper hashed passwords.
-- Or run:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('student123'))


-- ============================================================
-- Sample Results
-- ============================================================
INSERT INTO results (student_id, course_id, score) VALUES
(1, 1, 4),
(1, 2, 3),
(2, 1, 5),
(2, 3, 4),
(3, 5, 5);


-- ============================================================
-- Sample Feedback
-- ============================================================
INSERT INTO feedback (student_id, message, date) VALUES
(1, 'The Mathematics course is very helpful. The videos explain concepts very clearly. I am able to understand Number Systems much better now. Thank you!', '2024-01-15'),
(2, 'I love the Science videos. The quiz feature is excellent and helps me test my knowledge. Please add more questions to the quiz section.', '2024-01-16'),
(3, 'Computer Science basics course is outstanding. The notes are very well written and easy to download. The platform is very user friendly.', '2024-01-17');


-- ============================================================
-- ADMIN PASSWORD RESET HELPER
-- Run the Python code below to get proper hash, then update:
--
-- from werkzeug.security import generate_password_hash
-- hash = generate_password_hash('admin123')
-- Then run:
-- UPDATE admin SET password='<paste_hash_here>' WHERE username='admin';
-- ============================================================
