"""
Authentication decorators and session helpers.
"""
from functools import wraps
from flask import session, redirect, url_for, request, flash


def login_required(f):
    """
    Decorator to protect routes requiring authentication.
    Redirects unauthenticated users to login with a safe next URL parameter.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # For JSON API requests, return a clean 401 JSON error instead of redirecting
            if request.path.startswith('/api/') or request.is_json or request.headers.get('Accept') == 'application/json':
                return {'error': 'Authentication required', 'status': 401}, 401
                
            flash("Please log in to access this page.", "warning")
            # Store relative next path safely
            next_url = request.path
            if request.query_string:
                next_url += '?' + request.query_string.decode('utf-8')
            return redirect(url_for('auth.login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function
