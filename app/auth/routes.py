"""
Authentication routes: Register, Login, and Logout.
Uses Werkzeug password hashing and secure Flask sessions.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import query_db, execute_db, DatabaseError
from app.utils import validate_registration, is_safe_url

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    form_data = {
        'full_name': '',
        'email': ''
    }

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        form_data['full_name'] = full_name
        form_data['email'] = email

        # 1. Validate fields
        is_valid, error_msg = validate_registration(full_name, email, password, confirm_password)
        if not is_valid:
            flash(error_msg, "error")
            return render_template('auth/register.html', form=form_data)

        # 2. Check if email already exists
        try:
            existing_user = query_db("SELECT user_id FROM users WHERE email = %s;", (email,), one=True)
            if existing_user:
                flash("An account with this email address already exists.", "error")
                return render_template('auth/register.html', form=form_data)

            # 3. Hash password securely (never store or log plain text)
            pwd_hash = generate_password_hash(password, method='scrypt')

            # 4. Insert into MySQL
            user_id = execute_db(
                "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s);",
                (full_name, email, pwd_hash)
            )

            # 5. Log in automatically and redirect to dashboard
            session.clear()
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['user_email'] = email

            flash(f"Welcome to Home Budget, {full_name}! Your account has been created.", "success")
            return redirect(url_for('main.dashboard'))

        except DatabaseError as e:
            flash("Database error during registration. Please try again.", "error")
            return render_template('auth/register.html', form=form_data)

    return render_template('auth/register.html', form=form_data)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login with generic error messages and safe next redirection."""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    next_page = request.args.get('next', '')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_page = request.form.get('next', '')

        if not email or not password:
            flash("Invalid email or password.", "error")
            return render_template('auth/login.html', email=email, next=next_page)

        try:
            user = query_db(
                "SELECT user_id, full_name, email, password_hash FROM users WHERE email = %s;",
                (email,),
                one=True
            )

            # Generic error message to prevent user enumeration
            if not user or not check_password_hash(user['password_hash'], password):
                flash("Invalid email or password.", "error")
                return render_template('auth/login.html', email=email, next=next_page)

            # Login successful: establish session
            session.clear()
            session['user_id'] = user['user_id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']

            flash(f"Welcome back, {user['full_name']}!", "success")

            # Validate safe relative redirection
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))

        except DatabaseError:
            flash("Database temporarily unavailable. Please try again later.", "error")
            return render_template('auth/login.html', email=email, next=next_page)

    return render_template('auth/login.html', email='', next=next_page)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logs out user via secure POST request and clears session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('main.home'))
