"""
Configuration module for Home Budget application.
Reads environment variables from .env file using python-dotenv.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base application configuration class."""
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-please-change')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS

    # MySQL Database Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_NAME = os.environ.get('DB_NAME', 'home_budget_db')
    DB_USER = os.environ.get('DB_USER', 'budget_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

    # Localization
    CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '₹')
