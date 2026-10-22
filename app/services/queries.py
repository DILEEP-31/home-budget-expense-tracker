"""
Database Query Service for Home Budget Tracker.
Centralizes all parameterized SQL queries for transactions, categories, and analytics.
Prevents duplicate logic and strictly enforces parameterized SQL.
"""
from decimal import Decimal
from datetime import date
from app.db import query_db, execute_db


def get_category_spending_for_month(user_id, year, month):
    """
    Returns a dict mapping category_id -> Decimal(total_spent) for expenses in given month.
    """
    query = """
        SELECT category_id, COALESCE(SUM(amount), 0) AS total_spent
        FROM transactions
        WHERE user_id = %s
          AND transaction_type = 'expense'
          AND YEAR(transaction_date) = %s
          AND MONTH(transaction_date) = %s
        GROUP BY category_id;
    """
    rows = query_db(query, (user_id, year, month))
    return {r['category_id']: Decimal(str(r['total_spent'])) for r in rows}


def get_monthly_budgets(user_id, year, month):
    """
    Returns a dict mapping category_id -> Decimal(budget_amount) for given user/year/month.
    """
    query = """
        SELECT category_id, budget_amount
        FROM monthly_budgets
        WHERE user_id = %s AND budget_year = %s AND budget_month = %s;
    """
    rows = query_db(query, (user_id, year, month))
    return {r['category_id']: Decimal(str(r['budget_amount'])) for r in rows}


def save_monthly_budget(user_id, category_id, year, month, amount):
    """
    Saves or updates a monthly budget using INSERT ... ON DUPLICATE KEY UPDATE.
    """
    query = """
        INSERT INTO monthly_budgets (user_id, category_id, budget_year, budget_month, budget_amount)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE budget_amount = VALUES(budget_amount);
    """
    return execute_db(query, (user_id, category_id, year, month, amount))


def copy_budgets_from_previous_month(user_id, target_year, target_month):
    """
    Copies all budget limits from the previous month to the target month.
    Handles January -> December transition safely.
    Returns the number of copied budget limits.
    """
    if target_month == 1:
        prev_year = target_year - 1
        prev_month = 12
    else:
        prev_year = target_year
        prev_month = target_month - 1

    prev_budgets = get_monthly_budgets(user_id, prev_year, prev_month)
    if not prev_budgets:
        return 0

    copied_count = 0
    for cat_id, amount in prev_budgets.items():
        save_monthly_budget(user_id, cat_id, target_year, target_month, amount)
        copied_count += 1
    return copied_count


def apply_budgets_to_full_year(user_id, source_year, source_month):
    """
    Applies the source month's budget limits to all 12 months (1-12) of source_year.
    Returns the total updates applied.
    """
    source_budgets = get_monthly_budgets(user_id, source_year, source_month)
    if not source_budgets:
        return 0

    total_applied = 0
    for m in range(1, 13):
        for cat_id, amount in source_budgets.items():
            save_monthly_budget(user_id, cat_id, source_year, m, amount)
            total_applied += 1
    return total_applied


def get_yearly_budget_summary(user_id, year):
    """
    Calculates monthly totals (budget, spent, status) for each of the 12 months in the year,
    plus category-wise totals across the entire year.
    """
    from app.services.budget_logic import determine_budget_status

    # 1. Fetch all monthly budgets for the year
    budgets_query = """
        SELECT budget_month, category_id, budget_amount
        FROM monthly_budgets
        WHERE user_id = %s AND budget_year = %s;
    """
    budget_rows = query_db(budgets_query, (user_id, year))

    # 2. Fetch all expense transactions for the year
    expenses_query = """
        SELECT MONTH(transaction_date) AS t_month, category_id, COALESCE(SUM(amount), 0) AS total_spent
        FROM transactions
        WHERE user_id = %s AND transaction_type = 'expense' AND YEAR(transaction_date) = %s
        GROUP BY MONTH(transaction_date), category_id;
    """
    expense_rows = query_db(expenses_query, (user_id, year))

    # Month-by-month summary (1 to 12)
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    months_data = []
    yearly_total_budget = Decimal('0.00')
    yearly_total_spent = Decimal('0.00')

    for m in range(1, 13):
        m_budget = sum(Decimal(str(r['budget_amount'])) for r in budget_rows if r['budget_month'] == m)
        m_spent = sum(Decimal(str(r['total_spent'])) for r in expense_rows if r['t_month'] == m)
        status_info = determine_budget_status(m_spent, m_budget if m_budget > 0 else None)

        yearly_total_budget += m_budget
        yearly_total_spent += m_spent

        months_data.append({
            'month_num': m,
            'month_name': month_names[m - 1],
            'budget': m_budget,
            'spent': m_spent,
            **status_info
        })

    # Category-by-category yearly totals
    expense_cats, _ = get_categories_grouped()
    categories_yearly = []

    for cat in expense_cats:
        c_id = cat['category_id']
        c_budget = sum(Decimal(str(r['budget_amount'])) for r in budget_rows if r['category_id'] == c_id)
        c_spent = sum(Decimal(str(r['total_spent'])) for r in expense_rows if r['category_id'] == c_id)
        c_status = determine_budget_status(c_spent, c_budget if c_budget > 0 else None)

        categories_yearly.append({
            'category_id': c_id,
            'category_name': cat['category_name'],
            'color': cat['color'],
            'icon': cat['icon'],
            'yearly_budget': c_budget,
            'yearly_spent': c_spent,
            **c_status
        })

    yearly_status = determine_budget_status(yearly_total_spent, yearly_total_budget if yearly_total_budget > 0 else None)

    return {
        'year': year,
        'months': months_data,
        'categories': categories_yearly,
        'yearly_total_budget': yearly_total_budget,
        'yearly_total_spent': yearly_total_spent,
        'yearly_remaining': (yearly_total_budget - yearly_total_spent) if yearly_total_budget > 0 else None,
        'yearly_status': yearly_status
    }


def get_all_categories():
    """
    Retrieves all available categories ordered by type and name.
    Returns a list of dicts: [ {category_id, category_name, category_type, color, icon}, ... ]
    """
    query = """
        SELECT category_id, category_name, category_type, color, icon
        FROM categories
        ORDER BY category_type ASC, category_name ASC;
    """
    return query_db(query)


def get_categories_grouped():
    """
    Retrieves categories grouped into 'expense' and 'income' dictionaries.
    """
    cats = get_all_categories()
    expense_cats = [c for c in cats if c['category_type'] == 'expense']
    income_cats = [c for c in cats if c['category_type'] == 'income']
    return expense_cats, income_cats


def get_monthly_summary(user_id, year, month):
    """
    Calculates monthly financial metrics for a user:
    - Total Income
    - Total Expenses
    - Monthly Savings (Total Income - Total Expenses)
    - Savings Rate (Monthly Savings / Total Income; protected against divide-by-zero)
    - Total All-time Balance (All-time Income - All-time Expenses)
    - Transaction count for the selected month
    """
    # 1. Monthly Income & Expenses for selected month
    monthly_query = """
        SELECT 
            transaction_type,
            COALESCE(SUM(amount), 0) AS total_amount,
            COUNT(*) AS count
        FROM transactions
        WHERE user_id = %s
          AND YEAR(transaction_date) = %s
          AND MONTH(transaction_date) = %s
        GROUP BY transaction_type;
    """
    monthly_rows = query_db(monthly_query, (user_id, year, month))

    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')
    monthly_count = 0

    for row in monthly_rows:
        amount = Decimal(str(row['total_amount']))
        monthly_count += row['count']
        if row['transaction_type'] == 'income':
            total_income = amount
        elif row['transaction_type'] == 'expense':
            total_expenses = amount

    # Definitions per Section 5:
    # Monthly Savings = income minus expenses for the selected month
    monthly_savings = total_income - total_expenses

    # Savings Rate = monthly savings divided by monthly income (guard against divide-by-zero)
    if total_income > Decimal('0'):
        savings_rate = float((monthly_savings / total_income) * 100)
    else:
        savings_rate = 0.0

    # 2. All-Time Balance: all-time income minus all-time expenses
    all_time_query = """
        SELECT 
            transaction_type,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM transactions
        WHERE user_id = %s
        GROUP BY transaction_type;
    """
    all_time_rows = query_db(all_time_query, (user_id,))
    all_time_income = Decimal('0.00')
    all_time_expenses = Decimal('0.00')
    for row in all_time_rows:
        amount = Decimal(str(row['total_amount']))
        if row['transaction_type'] == 'income':
            all_time_income = amount
        elif row['transaction_type'] == 'expense':
            all_time_expenses = amount

    total_balance = all_time_income - all_time_expenses

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'monthly_savings': monthly_savings,
        'savings_rate': savings_rate,
        'total_balance': total_balance,
        'transaction_count': monthly_count
    }


def get_top_spending_categories(user_id, year, month, limit=5):
    """
    Retrieves the top expense categories for a given month,
    including total spent, percentage of total expenses, color, and icon.
    """
    query = """
        SELECT 
            c.category_id,
            c.category_name,
            c.color,
            c.icon,
            COALESCE(SUM(t.amount), 0) AS category_total
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
          AND t.transaction_type = 'expense'
          AND YEAR(t.transaction_date) = %s
          AND MONTH(t.transaction_date) = %s
        GROUP BY c.category_id, c.category_name, c.color, c.icon
        ORDER BY category_total DESC
        LIMIT %s;
    """
    rows = query_db(query, (user_id, year, month, limit))
    if not rows:
        return []

    # Calculate overall monthly expenses to determine accurate percentages
    total_spent = sum(Decimal(str(r['category_total'])) for r in rows)
    results = []
    for r in rows:
        cat_total = Decimal(str(r['category_total']))
        percentage = float((cat_total / total_spent) * 100) if total_spent > 0 else 0.0
        results.append({
            'category_id': r['category_id'],
            'category_name': r['category_name'],
            'color': r['color'],
            'icon': r['icon'],
            'total': cat_total,
            'percentage': round(percentage, 1)
        })
    return results


def get_recent_transactions(user_id, limit=5):
    """
    Retrieves the most recent transactions for the dashboard view.
    """
    query = """
        SELECT 
            t.transaction_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description,
            c.category_name,
            c.color,
            c.icon
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        ORDER BY t.transaction_date DESC, t.created_at DESC, t.transaction_id DESC
        LIMIT %s;
    """
    return query_db(query, (user_id, limit))


def get_transaction_by_id(user_id, transaction_id):
    """
    Retrieves a single transaction by ID, strictly checking user ownership.
    Returns None if not found or if it belongs to another user.
    """
    query = """
        SELECT 
            t.transaction_id,
            t.user_id,
            t.category_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description,
            c.category_name,
            c.color,
            c.icon
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.transaction_id = %s AND t.user_id = %s;
    """
    return query_db(query, (transaction_id, user_id), one=True)


def update_transaction(user_id, transaction_id, category_id, transaction_type, amount, transaction_date, description):
    """
    Updates an existing transaction, strictly matching user_id.
    """
    query = """
        UPDATE transactions
        SET category_id = %s,
            transaction_type = %s,
            amount = %s,
            transaction_date = %s,
            description = %s
        WHERE transaction_id = %s AND user_id = %s;
    """
    return execute_db(query, (category_id, transaction_type, amount, transaction_date, description, transaction_id, user_id))


def get_filtered_transactions(user_id, date_from=None, date_to=None, transaction_type=None,
                              category_id=None, min_amount=None, max_amount=None,
                              search_term=None, sort_by='date', sort_order='desc',
                              page=1, per_page=10):
    """
    Retrieves filtered, searched, sorted, and paginated transactions for a user.
    Uses strict parameterized queries for all WHERE conditions.
    Uses an explicit whitelist for ORDER BY columns to prevent SQL injection.
    Safely escapes wildcard characters (% and _) in search terms.
    Returns (records_list, total_count, total_pages, current_page).
    """
    # 1. Base conditions
    conditions = ["t.user_id = %s"]
    params = [user_id]

    # 2. Date filters
    if date_from:
        conditions.append("t.transaction_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("t.transaction_date <= %s")
        params.append(date_to)

    # 3. Transaction Type filter
    if transaction_type in ('income', 'expense'):
        conditions.append("t.transaction_type = %s")
        params.append(transaction_type)

    # 4. Category filter
    if category_id:
        conditions.append("t.category_id = %s")
        params.append(category_id)

    # 5. Amount range filters
    if min_amount is not None:
        conditions.append("t.amount >= %s")
        params.append(min_amount)
    if max_amount is not None:
        conditions.append("t.amount <= %s")
        params.append(max_amount)

    # 6. Description search with safe wildcard escaping
    if search_term and search_term.strip():
        # Escape MySQL LIKE wildcards so user input like '%', '_', or injection attempts are literal
        escaped_term = search_term.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        conditions.append("t.description LIKE %s")
        params.append(f"%{escaped_term}%")

    where_clause = " WHERE " + " AND ".join(conditions)

    # 7. Get Total Count of matching rows for pagination
    count_query = f"""
        SELECT COUNT(*) AS total
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        {where_clause};
    """
    count_result = query_db(count_query, tuple(params), one=True)
    total_count = count_result['total'] if count_result else 0

    # 8. Sort Column Whitelist (Rules Section 7)
    sort_column_whitelist = {
        'date': 't.transaction_date',
        'amount': 't.amount',
        'category': 'c.category_name',
        'type': 't.transaction_type'
    }
    order_column = sort_column_whitelist.get(sort_by, 't.transaction_date')
    order_direction = 'ASC' if str(sort_order).lower() == 'asc' else 'DESC'

    # Secondary tie-breaker sort for deterministic pagination
    order_by_clause = f"ORDER BY {order_column} {order_direction}, t.transaction_id DESC"

    # 9. Pagination calculations
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    per_page = int(per_page)
    total_pages = max(1, (total_count + per_page - 1) // per_page) if total_count > 0 else 1
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * per_page

    # 10. Fetch paginated records
    data_query = f"""
        SELECT 
            t.transaction_id,
            t.user_id,
            t.category_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description,
            c.category_name,
            c.color,
            c.icon
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        {where_clause}
        {order_by_clause}
        LIMIT %s OFFSET %s;
    """
    fetch_params = tuple(params) + (per_page, offset)
    records = query_db(data_query, fetch_params)

    return records, total_count, total_pages, page


def get_all_transactions(user_id, limit=50):
    """
    Retrieves the complete transaction history for the transactions page (newest first).
    """
    query = """
        SELECT 
            t.transaction_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description,
            c.category_name,
            c.color,
            c.icon
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        ORDER BY t.transaction_date DESC, t.created_at DESC, t.transaction_id DESC
        LIMIT %s;
    """
    return query_db(query, (user_id, limit))


def get_available_months(user_id):
    """
    Retrieves distinct Year-Month combinations with recorded transactions for selector.
    Always includes current month so the user can select it even before transactions exist.
    """
    query = """
        SELECT DISTINCT 
            YEAR(transaction_date) AS yr, 
            MONTH(transaction_date) AS mo
        FROM transactions
        WHERE user_id = %s
        ORDER BY yr DESC, mo DESC;
    """
    rows = query_db(query, (user_id,))
    today = date.today()
    months_list = [(r['yr'], r['mo']) for r in rows]
    current = (today.year, today.month)
    if current not in months_list:
        months_list.insert(0, current)
    return months_list


def get_distinct_transaction_years(user_id):
    """
    Retrieves distinct years with recorded transactions for a user.
    Always includes current year.
    """
    query = """
        SELECT DISTINCT YEAR(transaction_date) AS yr
        FROM transactions
        WHERE user_id = %s
        ORDER BY yr DESC;
    """
    rows = query_db(query, (user_id,))
    today_year = date.today().year
    years = [r['yr'] for r in rows if r['yr'] is not None]
    if today_year not in years:
        years.insert(0, today_year)
    return sorted(list(set(years)), reverse=True)


def create_transaction(user_id, category_id, transaction_type, amount, transaction_date, description):
    """
    Inserts a validated transaction into MySQL.
    """
    query = """
        INSERT INTO transactions 
            (user_id, category_id, transaction_type, amount, transaction_date, description)
        VALUES 
            (%s, %s, %s, %s, %s, %s);
    """
    return execute_db(query, (user_id, category_id, transaction_type, amount, transaction_date, description))


def delete_transaction(user_id, transaction_id):
    """
    Deletes a transaction belonging to the specified user.
    Enforces user_id matching to prevent deleting records of other users.
    """
    query = """
        DELETE FROM transactions
        WHERE transaction_id = %s AND user_id = %s;
    """
    return execute_db(query, (transaction_id, user_id))
