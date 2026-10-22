"""
Validation, Formatting, and Authentication utility helpers for Home Budget Tracker.
Provides reusable server-side validation functions suitable for unit testing.
"""
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from flask import session


def get_current_user_id():
    """
    Returns the active user ID from the authenticated session.
    Returns None if the user is unauthenticated.
    Every query throughout the application filters by this user_id.
    """
    return session.get('user_id')


def validate_registration(full_name, email, password, confirm_password):
    """
    Validates user registration fields:
    - Full name required (max 100 chars)
    - Valid email format (max 150 chars)
    - Password at least 8 chars, with at least one letter and one number
    - Passwords must match
    Returns (is_valid, error_message)
    """
    if not full_name or not str(full_name).strip():
        return False, "Full name is required."
    
    if len(str(full_name).strip()) > 100:
        return False, "Full name cannot exceed 100 characters."

    if not email or not str(email).strip():
        return False, "Email address is required."

    email_clean = str(email).strip().lower()
    if len(email_clean) > 150:
        return False, "Email address cannot exceed 150 characters."

    # Standard RFC-compliant email regex pattern
    email_regex = r'^[\w\.\+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$'
    if not re.match(email_regex, email_clean):
        return False, "Please enter a valid email address."

    if not password:
        return False, "Password is required."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
        return False, "Password must contain at least one letter and one number."

    if password != confirm_password:
        return False, "Passwords do not match."

    return True, None


def is_safe_url(target):
    """
    Ensures redirects stay strictly within the same host/app (relative URLs only).
    Prevents Open Redirect vulnerabilities.
    """
    if not target:
        return False
    # Must start with a single slash, not double slash (//evil.com) or backslash
    if target.startswith('/') and not target.startswith('//') and not target.startswith('/\\'):
        return True
    return False



def validate_transaction_type(t_type):
    """Validates that transaction_type is either 'income' or 'expense'."""
    if not t_type or t_type not in ('income', 'expense'):
        return False, "Transaction type must be either 'income' or 'expense'."
    return True, None


def validate_amount(amount_raw):
    """
    Validates amount:
    - Must be a valid number
    - Greater than 0
    - At most 9,999,999.99
    - Maximum 2 decimal places
    Returns (is_valid, parsed_decimal, error_message)
    """
    if amount_raw is None or str(amount_raw).strip() == '':
        return False, None, "Amount is required."

    try:
        val = Decimal(str(amount_raw).strip())
    except (InvalidOperation, ValueError, TypeError):
        return False, None, "Amount must be a valid number."

    if val <= Decimal('0'):
        return False, None, "Amount must be greater than 0."

    if val > Decimal('9999999.99'):
        return False, None, "Amount cannot exceed 9,999,999.99."

    # Verify maximum 2 decimal places
    # If exponent is negative, number of decimal digits is abs(exponent)
    exp = val.as_tuple().exponent
    if exp < -2:
        return False, None, "Amount cannot have more than 2 decimal places."

    return True, val, None


def validate_transaction_date(date_raw):
    """
    Validates transaction date:
    - Must be in YYYY-MM-DD format
    - Must not be in the future
    Returns (is_valid, parsed_date, error_message)
    """
    if not date_raw or str(date_raw).strip() == '':
        return False, None, "Transaction date is required."

    try:
        parsed_dt = datetime.strptime(str(date_raw).strip(), '%Y-%m-%d').date()
    except ValueError:
        return False, None, "Date must be a valid calendar date in YYYY-MM-DD format."

    today = date.today()
    if parsed_dt > today:
        return False, None, "Transaction date cannot be in the future."

    return True, parsed_dt, None


def validate_description(description_raw):
    """
    Validates description:
    - Optional
    - Trimmed
    - Maximum 255 characters
    Returns (is_valid, sanitized_desc, error_message)
    """
    if description_raw is None:
        return True, None, None

    sanitized = str(description_raw).strip()
    if len(sanitized) > 255:
        return False, None, "Description cannot exceed 255 characters."

    return True, (sanitized if sanitized else None), None


def validate_category_match(category_id_raw, t_type, categories_map):
    """
    Validates category:
    - Must exist in database
    - Category's category_type must match transaction_type
    :param category_id_raw: The submitted category ID
    :param t_type: 'income' or 'expense'
    :param categories_map: dict of category_id -> category dict
    Returns (is_valid, category_id, error_message)
    """
    if not category_id_raw:
        return False, None, "Please select a category."

    try:
        cat_id = int(category_id_raw)
    except (ValueError, TypeError):
        return False, None, "Invalid category selected."

    if cat_id not in categories_map:
        return False, None, "Selected category does not exist."

    cat = categories_map[cat_id]
    if cat.get('category_type') != t_type:
        return False, None, f"Selected category '{cat.get('category_name')}' does not match transaction type '{t_type}'."

    return True, cat_id, None


def format_currency(amount, symbol='₹'):
    """Formats numeric amount into localized currency string e.g. ₹65,000.00"""
    if amount is None:
        amount = 0.0
    return f"{symbol}{float(amount):,.2f}"


def format_date(val):
    """Formats a date object, datetime object, or ISO date string to '14 Oct 2026'."""
    if not val:
        return '—'
    if isinstance(val, (datetime, date)):
        return val.strftime('%d %b %Y')
    try:
        val_str = str(val).split('T')[0].split(' ')[0]
        dt = datetime.strptime(val_str, '%Y-%m-%d')
        return dt.strftime('%d %b %Y')
    except Exception:
        return str(val)
