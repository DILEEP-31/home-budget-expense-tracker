"""
Unit tests for server-side validation functions.
"""
from datetime import date, timedelta
from decimal import Decimal
import pytest
from app.utils import (
    validate_registration,
    validate_transaction_type,
    validate_amount,
    validate_transaction_date,
    validate_description,
    validate_category_match
)


def test_validate_registration_valid():
    is_valid, err = validate_registration("Jane Doe", "jane@example.com", "Password123", "Password123")
    assert is_valid is True
    assert err is None


def test_validate_registration_empty_name():
    is_valid, err = validate_registration("", "jane@example.com", "Password123", "Password123")
    assert is_valid is False
    assert "Full name is required" in err


def test_validate_registration_invalid_email():
    is_valid, err = validate_registration("Jane Doe", "not-an-email", "Password123", "Password123")
    assert is_valid is False
    assert "valid email" in err


def test_validate_registration_short_password():
    is_valid, err = validate_registration("Jane Doe", "jane@example.com", "Pass1", "Pass1")
    assert is_valid is False
    assert "at least 8 characters" in err


def test_validate_registration_password_missing_number():
    is_valid, err = validate_registration("Jane Doe", "jane@example.com", "PasswordOnly", "PasswordOnly")
    assert is_valid is False
    assert "at least one letter and one number" in err


def test_validate_registration_password_mismatch():
    is_valid, err = validate_registration("Jane Doe", "jane@example.com", "Password123", "Mismatch456")
    assert is_valid is False
    assert "do not match" in err


def test_validate_amount_valid():
    is_valid, parsed, err = validate_amount("250.75")
    assert is_valid is True
    assert parsed == Decimal('250.75')
    assert err is None


def test_validate_amount_zero_or_negative():
    is_valid, _, err = validate_amount("0")
    assert is_valid is False
    assert "greater than 0" in err

    is_valid, _, err = validate_amount("-50")
    assert is_valid is False
    assert "greater than 0" in err


def test_validate_amount_too_large():
    is_valid, _, err = validate_amount("10000000.00")
    assert is_valid is False
    assert "cannot exceed" in err


def test_validate_amount_invalid_format():
    is_valid, _, err = validate_amount("abc")
    assert is_valid is False
    assert "valid number" in err


def test_validate_transaction_date_valid():
    today_str = date.today().strftime('%Y-%m-%d')
    is_valid, parsed, err = validate_transaction_date(today_str)
    assert is_valid is True
    assert parsed == date.today()
    assert err is None


def test_validate_transaction_date_future():
    future_date = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
    is_valid, _, err = validate_transaction_date(future_date)
    assert is_valid is False
    assert "cannot be in the future" in err


def test_validate_transaction_date_invalid_format():
    is_valid, _, err = validate_transaction_date("32-13-2026")
    assert is_valid is False
    assert "YYYY-MM-DD format" in err


def test_validate_transaction_type():
    assert validate_transaction_type("income")[0] is True
    assert validate_transaction_type("expense")[0] is True
    assert validate_transaction_type("investment")[0] is False


def test_validate_description_valid():
    is_valid, sanitized, err = validate_description(" Grocery store purchase ")
    assert is_valid is True
    assert sanitized == "Grocery store purchase"
    assert err is None


def test_validate_description_too_long():
    long_desc = "A" * 256
    is_valid, _, err = validate_description(long_desc)
    assert is_valid is False
    assert "cannot exceed 255" in err


def test_validate_category_match():
    categories_map = {
        1: {'category_id': 1, 'category_name': 'Groceries', 'category_type': 'expense'},
        2: {'category_id': 2, 'category_name': 'Salary', 'category_type': 'income'}
    }
    # Matching expense category
    valid, cat_id, err = validate_category_match("1", "expense", categories_map)
    assert valid is True
    assert cat_id == 1
    assert err is None

    # Mismatch: using income category for expense transaction
    valid, _, err = validate_category_match("2", "expense", categories_map)
    assert valid is False
    assert "does not match" in err
