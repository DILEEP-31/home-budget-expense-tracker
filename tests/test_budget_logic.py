"""
Unit tests for budget status determination and budget amount validation.
Tests strict thresholds: Safe (<80%), Warning (80% to 99.9%), Exceeded (>=100%).
"""
from decimal import Decimal
from app.services.budget_logic import determine_budget_status, validate_budget_amount


def test_budget_status_safe_below_80_percent():
    # 3999 / 5000 = 79.98% -> Safe
    res = determine_budget_status(spent=3999, limit=5000)
    assert res['status'] == 'safe'
    assert res['percentage'] == 80.0  # rounded to 1 decimal
    assert res['remaining'] == Decimal('1001.00')


def test_budget_status_exact_80_percent_boundary():
    # Exactly 80.0% boundary -> Must be 'warning'
    res = determine_budget_status(spent=4000, limit=5000)
    assert res['status'] == 'warning'
    assert res['percentage'] == 80.0
    assert res['remaining'] == Decimal('1000.00')


def test_budget_status_warning_range():
    # 4500 / 5000 = 90% -> Warning
    res = determine_budget_status(spent=4500, limit=5000)
    assert res['status'] == 'warning'
    assert res['percentage'] == 90.0
    assert res['remaining'] == Decimal('500.00')


def test_budget_status_exact_100_percent_boundary():
    # Exactly 100.0% boundary -> Must be 'exceeded'
    res = determine_budget_status(spent=5000, limit=5000)
    assert res['status'] == 'exceeded'
    assert res['percentage'] == 100.0
    assert res['remaining'] == Decimal('0.00')
    assert res['over_amount'] == Decimal('0.00')


def test_budget_status_over_100_percent():
    # 5500 / 5000 = 110% -> Exceeded
    res = determine_budget_status(spent=5500, limit=5000)
    assert res['status'] == 'exceeded'
    assert res['percentage'] == 110.0
    assert float(res['remaining']) == -500.0
    assert float(res['over_amount']) == 500.0


def test_budget_status_no_limit_configured():
    res = determine_budget_status(spent=1200, limit=0)
    assert res['status'] == 'no_limit'
    assert res['percentage'] == 0.0
    assert res['remaining'] is None


def test_validate_budget_amount_valid():
    assert validate_budget_amount("0")[0] is True
    assert validate_budget_amount("5000.50")[0] is True
    assert validate_budget_amount("9999999.99")[0] is True
    assert validate_budget_amount("")[0] is True  # Blank defaults to 0.00


def test_validate_budget_amount_invalid():
    # Negative amount
    valid, _, err = validate_budget_amount("-100")
    assert valid is False
    assert "cannot be negative" in err

    # Over 9,999,999.99
    valid, _, err = validate_budget_amount("10000000.00")
    assert valid is False
    assert "cannot exceed 9,999,999.99" in err

    # Non-numeric
    valid, _, err = validate_budget_amount("abc")
    assert valid is False
    assert "valid number" in err
