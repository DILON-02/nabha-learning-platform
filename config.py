import os

# ===========================
# Base Directory
# ===========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# ===========================
# Flask Configuration
# ===========================
class Config:

    # Secret key for session management and CSRF protection
    # Change this to a strong random string in production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dlp_nabha_secret_key_2024_change_in_production')

    # ===========================
    # MySQL Database Configuration
    # ===========================
    MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER     = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB       = os.environ.get('MYSQL_DB', 'learning_platform')
    MYSQL_CURSORCLASS = 'DictCursor'  # Returns query results as dictionaries

    # ===========================
    # File Upload Configuration
    # ===========================

    # Folder where uploaded PDF notes are stored
    UPLOAD_NOTES_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'uploads', 'notes')

    # Folder where uploaded course images are stored
    UPLOAD_IMAGES_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'uploads', 'course_images')

    # Maximum upload file size: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Allowed file extensions for notes (PDF only)
    ALLOWED_NOTES_EXTENSIONS = {'pdf'}

    # Allowed file extensions for course images
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ===========================
    # Pagination
    # ===========================
    COURSES_PER_PAGE = 6
    VIDEOS_PER_PAGE  = 8
    NOTES_PER_PAGE   = 8


# ===========================
# Development Configuration
# ===========================
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


# ===========================
# Production Configuration
# ===========================
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    # In production, always use environment variables
    SECRET_KEY     = os.environ.get('SECRET_KEY')
    MYSQL_HOST     = os.environ.get('MYSQL_HOST')
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER     = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB       = os.environ.get('MYSQL_DB')


# ===========================
# Configuration Selector
# ===========================
config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig
}


# ===========================
# Helper: Allowed File Check
# ===========================
def allowed_notes_file(filename):
    """Check if the uploaded file is an allowed notes format (PDF)."""
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_NOTES_EXTENSIONS
    )


def allowed_image_file(filename):
    """Check if the uploaded file is an allowed image format."""
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS
    )
