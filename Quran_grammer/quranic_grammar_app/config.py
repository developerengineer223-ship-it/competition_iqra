import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    SESSION_PERMANENT = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Get base path - use instance folder for SQLite
    BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quranic_grammar_app', 'instance')
    
    # Create instance folder if it doesn't exist
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    # Use SQLite for development with full path to instance folder
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(INSTANCE_PATH, 'quran_grammar_db.sqlite').replace('\\', '/')
    )

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Production should use MySQL or PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost/quran_grammar_db'
    )

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
