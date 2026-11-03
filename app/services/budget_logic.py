"""
Budget business logic and usage calculation service for Home Budget Tracker.
Provides unit-testable functions for tracking category spending vs. budget limits,
calculating percentages, and determining alert status (Safe, Warning, Exceeded).
"""
from decimal import Decimal


def determine_budget_status(spent, limit):
    """
    Determines status based on spending vs limit.
    Rules:
      - Limit == 0 or None: 'no_limit'
      - Spent < 80% of limit: 'safe' (Green)
      - Spent between 80% and 99.99%: 'warning' (Amber)
      - Spent >= 100% of limit: 'exceeded' (Red)
    Returns (status, percentage, remaining, over_amount)
    """
    spent_dec = Decimal(str(spent or 0))
    if limit is None or Decimal(str(limit)) <= Decimal('0'):
        return {
            'status': 'no_limit',
            'percentage': 0.0,
            'remaining': None,
            'over_amount': Decimal('0.00'),
            'badge_class': 'bg-secondary-subtle text-secondary',
            'progress_class': 'bg-secondary'
        }

    limit_dec = Decimal(str(limit))
    percentage = float((spent_dec / limit_dec) * 100)
    remaining = limit_dec - spent_dec
    over_amount = (spent_dec - limit_dec) if spent_dec > limit_dec else Decimal('0.00')

    if percentage >= 100.0:
        status = 'exceeded'
        badge_class = 'bg-danger-subtle text-danger'
        progress_class = 'bg-danger'
    elif percentage >= 80.0:
        status = 'warning'
        badge_class = 'bg-warning-subtle text-warning'
        progress_class = 'bg-warning'
    else:
        status = 'safe'
        badge_class = 'bg-success-subtle text-success'
        progress_class = 'bg-success'

    return {
        'status': status,
        'percentage': round(percentage, 1),
        'remaining': remaining,
        'over_amount': over_amount,
        'badge_class': badge_class,
        'progress_class': progress_class
    }


def calculate_category_budgets(categories, budgets_map, spending_map):
    """
    Combines expense categories with their configured budgets and actual spending.
    Returns:
      category_list: list of category dicts with calculated budget metrics
      total_budget: sum of configured budget limits
      total_spent: sum of actual expenditures
      total_remaining: total_budget - total_spent
      total_percentage: total spending utilization
      alerts: list of categories currently in 'warning' or 'exceeded' status
    """
    category_list = []
    total_budget = Decimal('0.00')
    total_spent = Decimal('0.00')
    alerts = []

    for cat in categories:
        cat_id = cat['category_id']
        limit = budgets_map.get(cat_id)
        spent = spending_map.get(cat_id, Decimal('0.00'))

        metrics = determine_budget_status(spent, limit)

        if limit is not None and limit > Decimal('0'):
            total_budget += Decimal(str(limit))
        total_spent += Decimal(str(spent))

        cat_data = {
            'category_id': cat_id,
            'category_name': cat['category_name'],
            'color': cat.get('color', '#4F46E5'),
            'icon': cat.get('icon', 'bi-tag'),
            'limit': limit,
            'spent': spent,
            **metrics
        }
        category_list.append(cat_data)

        if metrics['status'] in ('warning', 'exceeded'):
            alerts.append(cat_data)

    total_metrics = determine_budget_status(total_spent, total_budget)

    return {
        'categories': category_list,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_remaining': (total_budget - total_spent) if total_budget > 0 else None,
        'total_percentage': total_metrics['percentage'],
        'total_status': total_metrics['status'],
        'alerts': alerts
    }


def validate_budget_amount(amount_raw):
    """
    Validates a budget limit input:
    - Must be a valid number
    - Greater than or equal to 0
    - Maximum 9,999,999.99
    - Maximum 2 decimal places
    Returns (is_valid, parsed_decimal, error_message)
    """
    if amount_raw is None or str(amount_raw).strip() == '':
        return True, Decimal('0.00'), None

    try:
        val = Decimal(str(amount_raw).strip())
    except Exception:
        return False, None, "Budget limit must be a valid number."

    if val < Decimal('0'):
        return False, None, "Budget limit cannot be negative."

    if val > Decimal('9999999.99'):
        return False, None, "Budget limit cannot exceed 9,999,999.99."

    exp = val.as_tuple().exponent
    if exp < -2:
        return False, None, "Budget limit cannot have more than 2 decimal places."

    return True, val, None


def get_spending_status(income, expenses):
    """Alias to analytics.get_spending_status."""
    from app.services.analytics import get_spending_status as gss
    return gss(income, expenses)

