"""Flask application factory"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    """Create and configure Flask application"""
    
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import models after db initialization
    from app.models import User, Surah, Ayah, Word, GrammarTag
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.quran import quran_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(quran_bp, url_prefix='/quran')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user from database"""
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            # Return None if user not found or error occurs
            return None
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return {'error': 'صفحہ نہیں ملا | Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return {'error': 'سرور میں خرابی | Internal server error'}, 500
    
    # Note: Database tables are created by run.py script
    # This prevents connection errors during app startup if database isn't ready
    
    return app
