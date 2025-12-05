from functools import wraps
from flask import session, redirect, url_for, flash, render_template
from App.models import User, Student, Staff
from App.database import db


def login_user(username, password):
    """Authenticate user and store in session"""
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    if user and user.check_password(password):
        session['user_id'] = user.user_id
        session['username'] = user.username
        session['role'] = user.role
        return user
    return None


def logout_user():
    """Clear user session"""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)


def get_current_user():
    """Get current logged in user from session"""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None


def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth_views.login_page'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth_views.login_page'))
        if session.get('role') != 'student':
            flash('Access denied: Students only', 'error')
            return redirect(url_for('auth_views.login_page'))
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    """Decorator to require staff role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth_views.login_page'))
        if session.get('role') != 'staff':
            flash('Access denied: Staff only', 'error')
            return redirect(url_for('auth_views.login_page'))
        return f(*args, **kwargs)
    return decorated_function
