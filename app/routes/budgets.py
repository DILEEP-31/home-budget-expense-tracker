"""
Budgets routes: Monthly budget setup, copy operations, yearly summaries, and alert banners.
"""
from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.auth.decorators import login_required
from app.utils import get_current_user_id, format_currency
from app.services.queries import (
    get_categories_grouped,
    get_category_spending_for_month,
    get_monthly_budgets,
    save_monthly_budget,
    copy_budgets_from_previous_month,
    apply_budgets_to_full_year,
    get_yearly_budget_summary
)
from app.services.budget_logic import (
    calculate_category_budgets,
    validate_budget_amount
)
from app.db import DatabaseError

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')


@budgets_bp.route('', methods=['GET'], strict_slashes=False)
@budgets_bp.route('/', methods=['GET'], strict_slashes=False)
@login_required
def monthly_budgets():
    """
    Monthly budgets management and usage tracking view.
    Lists all expense categories with current spending, limit input, and usage progress.
    """
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
        if month < 1 or month > 12:
            month = today.month
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    try:
        expense_cats, _ = get_categories_grouped()
        budgets_map = get_monthly_budgets(user_id, year, month)
        spending_map = get_category_spending_for_month(user_id, year, month)
    except DatabaseError:
        flash("Unable to load budget data from database.", "error")
        expense_cats, budgets_map, spending_map = [], {}, {}

    budget_data = calculate_category_budgets(expense_cats, budgets_map, spending_map)

    selected_date = date(year, month, 1)
    month_name = selected_date.strftime('%B %Y')

    return render_template(
        'budgets/index.html',
        year=year,
        month=month,
        month_name=month_name,
        budget_data=budget_data,
        currency_symbol=current_app.config['CURRENCY_SYMBOL']
    )


@budgets_bp.route('/save', methods=['POST'])
@login_required
def save_budgets():
    """
    Saves monthly limits for all expense categories in batch using INSERT ... ON DUPLICATE KEY UPDATE.
    """
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.form.get('year', today.year))
        month = int(request.form.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    expense_cats, _ = get_categories_grouped()

    saved_count = 0
    errors = []

    for cat in expense_cats:
        field_name = f"limit_{cat['category_id']}"
        raw_val = request.form.get(field_name, '').strip()

        is_valid, parsed_amount, err = validate_budget_amount(raw_val)
        if not is_valid:
            errors.append(f"{cat['category_name']}: {err}")
            continue

        try:
            save_monthly_budget(user_id, cat['category_id'], year, month, parsed_amount)
            saved_count += 1
        except DatabaseError as e:
            errors.append(f"Could not save {cat['category_name']}: {e}")

    if errors:
        for err in errors:
            flash(err, "error")
    else:
        flash(f"Successfully saved monthly budget limits for {len(expense_cats)} categories!", "success")

    return redirect(url_for('budgets.monthly_budgets', year=year, month=month))


@budgets_bp.route('/copy-previous', methods=['POST'])
@login_required
def copy_previous():
    """Copies all budget limits from the immediately preceding calendar month."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.form.get('year', today.year))
        month = int(request.form.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    try:
        copied = copy_budgets_from_previous_month(user_id, year, month)
        if copied > 0:
            flash(f"Copied {copied} category budget limits from the previous month!", "success")
        else:
            flash("No budget limits were configured in the previous month to copy.", "warning")
    except DatabaseError as e:
        flash(f"Database error during copy: {e}", "error")

    return redirect(url_for('budgets.monthly_budgets', year=year, month=month))


@budgets_bp.route('/apply-year', methods=['POST'])
@login_required
def apply_year():
    """Applies the current month's limits to all 12 months of the year."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.form.get('year', today.year))
        month = int(request.form.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    try:
        applied = apply_budgets_to_full_year(user_id, year, month)
        if applied > 0:
            flash(f"Successfully replicated budget limits to all 12 months of {year}!", "success")
        else:
            flash("Please set and save limits for this month before applying them to the full year.", "warning")
    except DatabaseError as e:
        flash(f"Database error during full-year application: {e}", "error")

    return redirect(url_for('budgets.monthly_budgets', year=year, month=month))


@budgets_bp.route('/yearly')
@login_required
def yearly_summary():
    """Displays annual budget overview with month-by-month and category-by-category cards."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
    except (ValueError, TypeError):
        year = today.year

    try:
        summary_data = get_yearly_budget_summary(user_id, year)
    except DatabaseError:
        flash("Could not retrieve yearly budget data.", "error")
        summary_data = {'year': year, 'months': [], 'categories': []}

    return render_template(
        'budgets/yearly.html',
        summary=summary_data,
        year=year,
        today_year=today.year,
        currency_symbol=current_app.config['CURRENCY_SYMBOL']
    )
