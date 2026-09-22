import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'videoqr-super-secret-key-change-in-prod-2026')
    
    # Storage paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'videos')
    QR_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'qr_codes')
    
    # Upload limits (Default: 500 MB)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 500)) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'mp4', 'webm', 'mov', 'mkv', 'avi', 'm4v'}
    ALLOWED_MIME_TYPES = {
        'video/mp4',
        'video/webm',
        'video/quicktime',
        'video/x-matroska',
        'video/x-msvideo',
        'video/x-m4v'
    }

    # Database configuration (MySQL by default, falls back to SQLite if MySQL is not configured or unavailable)
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'video_qr_db')
    
    # Check if explicit DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        if os.environ.get('USE_MYSQL', 'false').lower() in ('true', '1', 'yes'):
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
        else:
            # Safe default fallback for instant zero-config execution
            sqlite_path = os.path.join(BASE_DIR, 'video_qr.db')
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    } if 'mysql' in SQLALCHEMY_DATABASE_URI else {}

    # Domain / Base URL configuration
    # Can be 'auto' (detect from request or LAN IP), or an explicit URL like 'https://video.yourdomain.com'
    BASE_URL = os.environ.get('BASE_URL', '').rstrip('/')
    
    # Default Admin Credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
