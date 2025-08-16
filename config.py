import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_SECRET = os.environ.get('SESSION_SECRET') or SECRET_KEY
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://ipam_user:ipam_password@localhost:5432/ipam_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'options': '-c timezone=Europe/Istanbul'
        }
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTForms configuration
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_ENABLED = True
    
    # Flask-Login configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Application configuration
    APP_NAME = os.environ.get('APP_NAME') or 'IPAM Platform'
    APP_PORT = int(os.environ.get('APP_PORT', 5000))
    APP_HOST = os.environ.get('APP_HOST') or '0.0.0.0'
    
    # Locale configuration
    DEFAULT_LOCALE = os.environ.get('DEFAULT_LOCALE') or 'tr_TR'
    TIMEZONE = os.environ.get('TIMEZONE') or 'Europe/Istanbul'
    BABEL_DEFAULT_LOCALE = 'tr'
    BABEL_DEFAULT_TIMEZONE = TIMEZONE
    
    # Exchange rate API configuration
    EXCHANGE_RATE_API_KEY = os.environ.get('EXCHANGE_RATE_API_KEY')
    EXCHANGE_RATE_API_URL = os.environ.get('EXCHANGE_RATE_API_URL') or \
        'https://api.exchangerate-api.com/v4/latest/'
    EXCHANGE_RATE_CACHE_HOURS = 24
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    
    # Allow HTTP in development
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Disable login for testing
    LOGIN_DISABLED = True


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Security hardening for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Get database URL from environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        # Fix for SQLAlchemy compatibility
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Production logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'WARNING'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env, config['default'])
