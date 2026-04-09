"""Custom decorators for access control"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required_custom(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not current_user.is_authenticated:
                flash('براہ کرم پہلے لاگ ان کریں | Please login first', 'warning')
                return redirect(url_for('auth.login'))
        except Exception as e:
            # If there's an error checking auth, redirect to login
            flash('براہ کرم پہلے لاگ ان کریں | Please login first', 'warning')
            return redirect(url_for('auth.login'))
        
        try:
            return f(*args, **kwargs)
        except Exception as e:
            flash(f'خرابی واقع ہوئی | An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.index'))
    
    return decorated_function
