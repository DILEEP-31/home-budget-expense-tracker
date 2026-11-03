"""
Main blueprint routes for Home Budget application.
Connects HTTP views to services/queries.py and handles server-side validation.
"""
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, abort
from app.auth.decorators import login_required
from app.utils import (
    get_current_user_id,
    validate_transaction_type,
    validate_amount,
    validate_transaction_date,
    validate_description,
    validate_category_match,
    format_currency
)
from app.services.queries import (
    get_all_categories,
    get_categories_grouped,
    get_monthly_summary,
    get_top_spending_categories,
    get_recent_transactions,
    get_all_transactions,
    get_available_months,
    create_transaction,
    delete_transaction
)
from app.db import DatabaseError

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Public standalone landing page (no sidebar, no dashboard cards)."""
    return render_template('landing.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Public login route mapping to auth.login."""
    from app.auth.routes import login as auth_login
    return auth_login()


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Public register route mapping to auth.register."""
    from app.auth.routes import register as auth_register
    return auth_register()


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Financial dashboard view.
    Accepts optional ?month=MM&year=YYYY query parameters, defaulting to the current month.
    Calculates summary cards, top spending categories, and recent transactions from MySQL.
    """
    user_id = get_current_user_id()
    today = date.today()

    # Read selected month/year or fallback to current
    try:
        month_year_param = request.args.get('month_year', '').strip()
        if month_year_param and '-' in month_year_param:
            parts = month_year_param.split('-')
            selected_year = int(parts[0])
            selected_month = int(parts[1])
        else:
            selected_year = int(request.args.get('year', today.year))
            selected_month = int(request.args.get('month', today.month))
        if selected_month < 1 or selected_month > 12:
            selected_month = today.month
    except (ValueError, TypeError):
        selected_year = today.year
        selected_month = today.month

    try:
        # Fetch metrics, budget tracking, and lists
        summary = get_monthly_summary(user_id, selected_year, selected_month)
        top_categories = get_top_spending_categories(user_id, selected_year, selected_month, limit=5)
        recent_txs = get_recent_transactions(user_id, limit=5)
        available_months = get_available_months(user_id)

        # Budget usage & alerts for current month
        from app.services.queries import get_monthly_budgets, get_category_spending_for_month
        from app.services.budget_logic import calculate_category_budgets
        expense_cats, _ = get_categories_grouped()
        budgets_map = get_monthly_budgets(user_id, selected_year, selected_month)
        spending_map = get_category_spending_for_month(user_id, selected_year, selected_month)
        budget_overview = calculate_category_budgets(expense_cats, budgets_map, spending_map)

        # Smart analytics insights & macro spending status
        from app.services.analytics import get_analytics_insights, get_spending_status
        insights_data = get_analytics_insights(user_id, selected_year, selected_month)
        spending_status = get_spending_status(summary['total_income'], summary['total_expenses'])
    except DatabaseError as e:
        flash("Database temporarily unavailable. Please verify MySQL service is running.", "error")
        return render_template('dashboard.html', error_state=True, currency_symbol=current_app.config['CURRENCY_SYMBOL'])

    # Format month name for title display e.g. "October 2026"
    selected_date_obj = date(selected_year, selected_month, 1)
    month_name = selected_date_obj.strftime('%B %Y')

    return render_template(
        'dashboard.html',
        summary=summary,
        top_categories=top_categories,
        recent_txs=recent_txs,
        available_months=available_months,
        selected_year=selected_year,
        selected_month=selected_month,
        month_name=month_name,
        budget_overview=budget_overview,
        insights_data=insights_data,
        spending_status=spending_status,
        currency_symbol=current_app.config['CURRENCY_SYMBOL']
    )


@main_bp.route('/transactions')
@login_required
def transactions_list():
    """
    Displays historical transactions list with filters, search, sorting, and pagination.
    """
    from app.services.queries import get_filtered_transactions
    user_id = get_current_user_id()

    # Read filter query parameters
    date_from = request.args.get('date_from', '').strip() or None
    date_to = request.args.get('date_to', '').strip() or None
    t_type = request.args.get('type', '').strip().lower() or None
    if t_type not in ('income', 'expense'):
        t_type = None

    cat_id_raw = request.args.get('category_id', '').strip()
    try:
        category_id = int(cat_id_raw) if cat_id_raw else None
    except (ValueError, TypeError):
        category_id = None

    min_amount_raw = request.args.get('min_amount', '').strip()
    try:
        min_amount = float(min_amount_raw) if min_amount_raw else None
    except (ValueError, TypeError):
        min_amount = None

    max_amount_raw = request.args.get('max_amount', '').strip()
    try:
        max_amount = float(max_amount_raw) if max_amount_raw else None
    except (ValueError, TypeError):
        max_amount = None

    search_term = request.args.get('search', '').strip() or None
    sort_by = request.args.get('sort_by', 'date').strip().lower()
    sort_order = request.args.get('sort_order', 'desc').strip().lower()
    page_raw = request.args.get('page', 1)

    try:
        all_categories = get_all_categories()
        transactions, total_count, total_pages, current_page = get_filtered_transactions(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            transaction_type=t_type,
            category_id=category_id,
            min_amount=min_amount,
            max_amount=max_amount,
            search_term=search_term,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page_raw,
            per_page=10
        )
    except DatabaseError:
        flash("Unable to load transactions from the database.", "error")
        all_categories = []
        transactions, total_count, total_pages, current_page = [], 0, 1, 1

    # Check if any filter is active
    has_active_filters = bool(date_from or date_to or t_type or category_id or min_amount is not None or max_amount is not None or search_term)

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        all_categories=all_categories,
        total_count=total_count,
        total_pages=total_pages,
        current_page=current_page,
        has_active_filters=has_active_filters,
        filters={
            'date_from': date_from or '',
            'date_to': date_to or '',
            'type': t_type or '',
            'category_id': category_id or '',
            'min_amount': min_amount_raw or '',
            'max_amount': max_amount_raw or '',
            'search': search_term or '',
            'sort_by': sort_by,
            'sort_order': sort_order
        },
        currency_symbol=current_app.config['CURRENCY_SYMBOL']
    )


@main_bp.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """
    Form view and submission handler for editing an existing transaction.
    Verifies ownership and returns 404 if not found or belongs to another user.
    """
    from app.services.queries import get_transaction_by_id, update_transaction
    user_id = get_current_user_id()

    tx = get_transaction_by_id(user_id, transaction_id)
    if not tx:
        abort(404)

    try:
        all_categories = get_all_categories()
        expense_cats, income_cats = get_categories_grouped()
        categories_map = {c['category_id']: c for c in all_categories}
    except DatabaseError:
        flash("Database error while loading categories.", "error")
        return redirect(url_for('main.transactions_list'))

    # Form defaults from existing transaction
    form_data = {
        'transaction_type': tx['transaction_type'],
        'category_id': str(tx['category_id']),
        'amount': str(tx['amount']),
        'transaction_date': tx['transaction_date'].strftime('%Y-%m-%d') if hasattr(tx['transaction_date'], 'strftime') else str(tx['transaction_date']),
        'description': tx['description'] or ''
    }

    if request.method == 'POST':
        t_type = request.form.get('transaction_type', '').strip().lower()
        cat_id_raw = request.form.get('category_id', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        date_raw = request.form.get('transaction_date', '').strip()
        desc_raw = request.form.get('description', '')

        form_data.update({
            'transaction_type': t_type,
            'category_id': cat_id_raw,
            'amount': amount_raw,
            'transaction_date': date_raw,
            'description': desc_raw
        })

        # 1. Validate Transaction Type
        valid_type, err_type = validate_transaction_type(t_type)
        if not valid_type:
            flash(err_type, 'error')
            return render_template('transactions/edit.html', form=form_data, tx=tx, expense_cats=expense_cats, income_cats=income_cats)

        # 2. Validate Category Match
        valid_cat, cat_id, err_cat = validate_category_match(cat_id_raw, t_type, categories_map)
        if not valid_cat:
            flash(err_cat, 'error')
            return render_template('transactions/edit.html', form=form_data, tx=tx, expense_cats=expense_cats, income_cats=income_cats)

        # 3. Validate Amount
        valid_amount, parsed_amount, err_amount = validate_amount(amount_raw)
        if not valid_amount:
            flash(err_amount, 'error')
            return render_template('transactions/edit.html', form=form_data, tx=tx, expense_cats=expense_cats, income_cats=income_cats)

        # 4. Validate Date
        valid_date, parsed_date, err_date = validate_transaction_date(date_raw)
        if not valid_date:
            flash(err_date, 'error')
            return render_template('transactions/edit.html', form=form_data, tx=tx, expense_cats=expense_cats, income_cats=income_cats)

        # 5. Validate Description
        valid_desc, sanitized_desc, err_desc = validate_description(desc_raw)
        if not valid_desc:
            flash(err_desc, 'error')
            return render_template('transactions/edit.html', form=form_data, tx=tx, expense_cats=expense_cats, income_cats=income_cats)

        # Update in MySQL
        try:
            update_transaction(
                user_id=user_id,
                transaction_id=transaction_id,
                category_id=cat_id,
                transaction_type=t_type,
                amount=parsed_amount,
                transaction_date=parsed_date,
                description=sanitized_desc
            )
            flash(f"Transaction #{transaction_id} updated successfully!", "success")
            return redirect(url_for('main.transactions_list'))
        except DatabaseError as e:
            flash(f"Failed to update transaction: {str(e)}", "error")
            return render_template('transactions/edit.html', form=form_data, tx=tx, expense_cats=expense_cats, income_cats=income_cats)

    return render_template(
        'transactions/edit.html',
        form=form_data,
        tx=tx,
        expense_cats=expense_cats,
        income_cats=income_cats,
        today_date=date.today().strftime('%Y-%m-%d')
    )


@main_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """
    Form view and submission handler for recording new transactions.
    Performs comprehensive server-side validation.
    """
    user_id = get_current_user_id()

    try:
        all_categories = get_all_categories()
        expense_cats, income_cats = get_categories_grouped()
        categories_map = {c['category_id']: c for c in all_categories}
    except DatabaseError:
        flash("Database error while loading categories.", "error")
        return redirect(url_for('main.transactions_list'))

    # Prepare form state to preserve user input on validation error
    form_data = {
        'transaction_type': 'expense',
        'category_id': '',
        'amount': '',
        'transaction_date': date.today().strftime('%Y-%m-%d'),
        'description': ''
    }

    if request.method == 'POST':
        # Retrieve form values
        t_type = request.form.get('transaction_type', '').strip().lower()
        cat_id_raw = request.form.get('category_id', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        date_raw = request.form.get('transaction_date', '').strip()
        desc_raw = request.form.get('description', '')

        form_data.update({
            'transaction_type': t_type,
            'category_id': cat_id_raw,
            'amount': amount_raw,
            'transaction_date': date_raw,
            'description': desc_raw
        })

        # 1. Validate Transaction Type
        valid_type, err_type = validate_transaction_type(t_type)
        if not valid_type:
            flash(err_type, 'error')
            return render_template('transactions/new.html', form=form_data, expense_cats=expense_cats, income_cats=income_cats)

        # 2. Validate Category Match
        valid_cat, cat_id, err_cat = validate_category_match(cat_id_raw, t_type, categories_map)
        if not valid_cat:
            flash(err_cat, 'error')
            return render_template('transactions/new.html', form=form_data, expense_cats=expense_cats, income_cats=income_cats)

        # 3. Validate Amount
        valid_amount, parsed_amount, err_amount = validate_amount(amount_raw)
        if not valid_amount:
            flash(err_amount, 'error')
            return render_template('transactions/new.html', form=form_data, expense_cats=expense_cats, income_cats=income_cats)

        # 4. Validate Date
        valid_date, parsed_date, err_date = validate_transaction_date(date_raw)
        if not valid_date:
            flash(err_date, 'error')
            return render_template('transactions/new.html', form=form_data, expense_cats=expense_cats, income_cats=income_cats)

        # 5. Validate Description
        valid_desc, sanitized_desc, err_desc = validate_description(desc_raw)
        if not valid_desc:
            flash(err_desc, 'error')
            return render_template('transactions/new.html', form=form_data, expense_cats=expense_cats, income_cats=income_cats)

        # All validations passed -> Insert into MySQL
        try:
            create_transaction(
                user_id=user_id,
                category_id=cat_id,
                transaction_type=t_type,
                amount=parsed_amount,
                transaction_date=parsed_date,
                description=sanitized_desc
            )
            flash(f"Successfully recorded {t_type} of {format_currency(parsed_amount, current_app.config['CURRENCY_SYMBOL'])}!", "success")
            return redirect(url_for('main.transactions_list'))
        except DatabaseError as e:
            flash(f"Failed to record transaction: {str(e)}", "error")
            return render_template('transactions/new.html', form=form_data, expense_cats=expense_cats, income_cats=income_cats)

    return render_template(
        'transactions/new.html',
        form=form_data,
        expense_cats=expense_cats,
        income_cats=income_cats,
        today_date=date.today().strftime('%Y-%m-%d')
    )


@main_bp.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction_route(transaction_id):
    """
    Deletes a transaction via secure POST request.
    Verifies ownership using get_current_user_id().
    If the transaction does not exist or belongs to another user, returns 404.
    """
    from app.db import query_db
    user_id = get_current_user_id()

    # Check existence and ownership
    existing = query_db(
        "SELECT transaction_id, user_id FROM transactions WHERE transaction_id = %s;",
        (transaction_id,),
        one=True
    )
    if not existing or existing['user_id'] != user_id:
        abort(404)

    try:
        affected = delete_transaction(user_id=user_id, transaction_id=transaction_id)
        if affected > 0:
            flash("Transaction successfully deleted.", "success")
        else:
            abort(404)
    except DatabaseError as e:
        flash(f"Error deleting record: {str(e)}", "error")

    return redirect(url_for('main.transactions_list'))


@main_bp.route('/transactions/export')
@login_required
def export_transactions_csv():
    """
    Exports filtered or all transactions for the logged-in user as a CSV file using Pandas.
    """
    import io
    import pandas as pd
    from flask import Response

    from app.services.queries import get_filtered_transactions

    user_id = get_current_user_id()
    date_from = request.args.get('date_from', '').strip() or None
    date_to = request.args.get('date_to', '').strip() or None
    t_type = request.args.get('type', '').strip().lower() or None
    if t_type not in ('income', 'expense'):
        t_type = None

    cat_id_raw = request.args.get('category_id', '').strip()
    try:
        cat_id = int(cat_id_raw) if cat_id_raw else None
    except (ValueError, TypeError):
        cat_id = None

    min_amount_raw = request.args.get('min_amount', '').strip()
    try:
        min_amount = float(min_amount_raw) if min_amount_raw else None
    except (ValueError, TypeError):
        min_amount = None

    max_amount_raw = request.args.get('max_amount', '').strip()
    try:
        max_amount = float(max_amount_raw) if max_amount_raw else None
    except (ValueError, TypeError):
        max_amount = None

    search_term = request.args.get('search', '').strip() or None
    sort_by = request.args.get('sort_by', 'date').strip().lower()
    sort_order = request.args.get('sort_order', 'desc').strip().lower()

    transactions, _, _, _ = get_filtered_transactions(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        transaction_type=t_type,
        category_id=cat_id,
        min_amount=min_amount,
        max_amount=max_amount,
        search_term=search_term,
        sort_by=sort_by,
        sort_order=sort_order,
        page=1,
        per_page=100000
    )

    rows = []
    for tx in transactions:
        rows.append({
            'Transaction ID': tx['transaction_id'],
            'Date': tx['transaction_date'].strftime('%Y-%m-%d') if hasattr(tx['transaction_date'], 'strftime') else str(tx['transaction_date']),
            'Type': tx['transaction_type'].capitalize(),
            'Category': tx['category_name'],
            'Amount (INR)': float(tx['amount']),
            'Description': tx['description'] or ''
        })

    if rows:
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(columns=['Transaction ID', 'Date', 'Type', 'Category', 'Amount (INR)', 'Description'])

    out = io.StringIO()
    df.to_csv(out, index=False)
    
    filename = f"transactions_export_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@main_bp.route('/categories')
@login_required
def categories_list():
    """
    Read-only category showcase from MySQL grouped by income and expense.
    """
    try:
        expense_cats, income_cats = get_categories_grouped()
    except DatabaseError:
        flash("Could not load categories from MySQL.", "error")
        expense_cats, income_cats = [], []

    return render_template(
        'categories/index.html',
        expense_cats=expense_cats,
        income_cats=income_cats
    )


@main_bp.route('/health')
def health_check():
    """Health check endpoint verifying application and MySQL status."""
    from app.db import query_db
    try:
        result = query_db("SELECT 1 AS status;", one=True)
        if result and result.get('status') == 1:
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "message": "MySQL connection successful"
            }), 200
        return jsonify({"status": "degraded", "database": "unexpected_result"}), 500
    except DatabaseError as e:
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500
    except Exception:
        return jsonify({"status": "unhealthy", "database": "error", "error": "Internal connection error"}), 500
