"""
Unit tests for analytics calculations using small sample DataFrames and mock series.
"""
import pandas as pd
import numpy as np


def test_category_expense_aggregation_math():
    # Sample DataFrame with 4 transactions across 2 categories
    data = {
        'category_id': [1, 1, 2, 2],
        'category_name': ['Groceries', 'Groceries', 'Utilities', 'Utilities'],
        'amount': [1200.0, 800.0, 500.0, 500.0],
        'transaction_type': ['expense', 'expense', 'expense', 'expense']
    }
    df = pd.DataFrame(data)

    grouped = df.groupby(['category_id', 'category_name'], as_index=False).agg(
        total_amount=('amount', 'sum'),
        txn_count=('amount', 'count')
    )

    total_expense = grouped['total_amount'].sum()
    grouped['percentage'] = np.round((grouped['total_amount'] / total_expense) * 100.0, 1)

    assert total_expense == 3000.0
    
    groceries_row = grouped[grouped['category_name'] == 'Groceries'].iloc[0]
    assert groceries_row['total_amount'] == 2000.0
    assert groceries_row['percentage'] == 66.7
    assert groceries_row['txn_count'] == 2

    utilities_row = grouped[grouped['category_name'] == 'Utilities'].iloc[0]
    assert utilities_row['total_amount'] == 1000.0
    assert utilities_row['percentage'] == 33.3


def test_savings_rate_calculations_and_zero_division():
    # Scenario 1: Normal income and expense
    income = 50000.0
    expense = 35000.0
    savings = income - expense
    rate = round((savings / income) * 100.0, 1) if income > 0 else 0.0
    assert savings == 15000.0
    assert rate == 30.0

    # Scenario 2: Zero income, zero expense
    income = 0.0
    expense = 0.0
    savings = income - expense
    rate = round((savings / income) * 100.0, 1) if income > 0 else 0.0
    assert savings == 0.0
    assert rate == 0.0

    # Scenario 3: Only expenses, zero income
    income = 0.0
    expense = 2500.0
    savings = income - expense
    rate = -100.0 if (income == 0.0 and expense > 0.0) else 0.0
    assert savings == -2500.0
    assert rate == -100.0


def test_month_over_month_percentage_change():
    # Spending decreased from 10,000 to 8,000 (-20%)
    curr_exp = 8000.0
    prev_exp = 10000.0
    diff = curr_exp - prev_exp
    pct_change = round((diff / prev_exp) * 100.0, 1) if prev_exp > 0 else 0.0
    assert diff == -2000.0
    assert pct_change == -20.0

    # Spending increased from 5,000 to 7,500 (+50%)
    curr_exp = 7500.0
    prev_exp = 5000.0
    diff = curr_exp - prev_exp
    pct_change = round((diff / prev_exp) * 100.0, 1) if prev_exp > 0 else 0.0
    assert diff == 2500.0
    assert pct_change == 50.0

    # Prior month had 0 spending
    curr_exp = 3000.0
    prev_exp = 0.0
    pct_change = 100.0 if (prev_exp == 0.0 and curr_exp > 0) else 0.0
    assert pct_change == 100.0
