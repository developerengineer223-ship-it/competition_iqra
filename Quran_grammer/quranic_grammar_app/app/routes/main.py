"""Main routes blueprint"""
from flask import Blueprint, render_template, session
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage route"""
    try:
        # Set default language if not set
        if 'language' not in session:
            if current_user.is_authenticated:
                session['language'] = current_user.language_preference
            else:
                session['language'] = 'en'  # Default to English
    except Exception as e:
        # Fallback to English if any error
        session['language'] = 'en'
    
    return render_template('index.html', title='Home')

@main_bp.route('/about')
def about():
    """About page"""
    try:
        if 'language' not in session:
            if current_user.is_authenticated:
                session['language'] = current_user.language_preference
            else:
                session['language'] = 'en'
    except Exception as e:
        session['language'] = 'en'
    
    return render_template('about.html', title='About')
