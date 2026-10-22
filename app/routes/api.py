"""
API Routes for Chart.js interactive charts and dynamic financial insights.
Strictly scoped to the authenticated user via @login_required.
Returns clean JSON responses with proper error handling and status codes.
"""
from datetime import date
from flask import Blueprint, jsonify, request
from app.auth.decorators import login_required
from app.utils import get_current_user_id
from app.services.analytics import (
    get_category_expense_breakdown,
    get_monthly_income_expense_summary,
    get_savings_trend,
    get_budget_utilization_analytics,
    get_analytics_insights
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/charts/category-breakdown')
@login_required
def chart_category_breakdown():
    """Returns category-wise expense distribution for Chart.js doughnut chart."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year)) if request.args.get('year') else None
        month = int(request.args.get('month', today.month)) if request.args.get('month') else None
    except (ValueError, TypeError):
        year, month = today.year, today.month

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    data = get_category_expense_breakdown(
        user_id, 
        year=year, 
        month=month, 
        start_date=start_date, 
        end_date=end_date
    )
    return jsonify(data)


@api_bp.route('/charts/monthly-summary')
@login_required
def chart_monthly_summary():
    """Returns 12-month income vs expense vs savings for Chart.js grouped bar chart."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
    except (ValueError, TypeError):
        year = today.year

    data = get_monthly_income_expense_summary(user_id, year=year)
    return jsonify(data)


@api_bp.route('/charts/savings-trend')
@login_required
def chart_savings_trend():
    """Returns monthly and cumulative savings progression for Chart.js line chart."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
    except (ValueError, TypeError):
        year = today.year

    data = get_savings_trend(user_id, year=year)
    return jsonify(data)


@api_bp.route('/charts/budget-usage')
@login_required
def chart_budget_usage():
    """Returns category budget utilization for Chart.js horizontal bar chart."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    data = get_budget_utilization_analytics(user_id, year, month)
    return jsonify(data)


@api_bp.route('/insights')
@login_required
def financial_insights():
    """Returns textual smart insights for the dashboard and analysis views."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    data = get_analytics_insights(user_id, year=year, month=month)
    return jsonify(data)
