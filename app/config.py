"""
Configuration module for Home Budget application.
Reads environment variables from .env file using python-dotenv.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Public Site & Project Contact Information
# Stored in one single place so contact details can be modified without changing HTML
SITE_INFO = {
    'name': 'P. Dileep',
    'phone': '9959845857',
    'phone_link': 'tel:+919959845857',
    'tel_link': 'tel:+919959845857',
    'email': 'dileepmbu@gmail.com',
    'email_link': 'mailto:dileepmbu@gmail.com',
    'initials': 'PD',
    'role': 'Project contact'
}


class Config:
    """Base application configuration class."""
    # Site Info
    SITE_INFO = SITE_INFO

    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-please-change')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Automatically enable Secure cookies in production (Render uses HTTPS by default)
    SESSION_COOKIE_SECURE = os.environ.get('RENDER', '').lower() == 'true' or os.environ.get('FLASK_ENV') == 'production'

    # MySQL Database Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_NAME = os.environ.get('DB_NAME', 'home_budget_db')
    DB_USER = os.environ.get('DB_USER', 'budget_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

    # Database Mode: If USE_SQLITE is true or when running on Render without cloud MySQL
    USE_SQLITE = os.environ.get('USE_SQLITE', '').lower() == 'true' or (
        os.environ.get('RENDER', '').lower() == 'true' and os.environ.get('DB_HOST') in (None, '', 'localhost')
    )
    SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'home_budget.db'))

    # Localization
    CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '₹')
