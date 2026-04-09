"""Authentication routes blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration is disabled - No new users can register"""
    flash('رجسٹریشن نظام بند ہے | Registration system is closed. No new users can register.', 'warning')
    return redirect(url_for('main.index'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login disabled - Direct access to all content"""
    flash('لاگ ان کی ضرورت نہیں | Login is not required. Enjoy full access!', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/logout')
def logout():
    """Logout - no-op (no authentication required)"""
    flash('شکریہ! براہ کرم دوبارہ ملاقات کریں | Thank you! See you next time!', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/set-language/<language>')
def set_language(language):
    """Set user language preference"""
    try:
        if language not in ['en', 'ur']:
            language = 'en'
        
        session['language'] = language
        
        # If user is logged in, update database
        if current_user.is_authenticated:
            try:
                current_user.language_preference = language
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Still continue even if db update fails
                pass
    
    except Exception as e:
        flash(f'زبان تبدیل میں خرابی | Error changing language: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('main.index'))
