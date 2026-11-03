"""
Analytics service using Pandas and NumPy.
Processes user transactions, calculates statistics (aggregations, percentages, averages, savings rate),
and handles edge cases such as empty datasets and divide-by-zero safely.
All numeric values are converted to standard float for JSON serialization.
"""
from datetime import date
from decimal import Decimal
import pandas as pd
import numpy as np
from app.db import query_db


def get_user_transactions_df(user_id, start_date=None, end_date=None, year=None, month=None):
    """
    Loads transactions for a given user from MySQL into a clean Pandas DataFrame.
    Filters by date range or year/month if specified.
    """
    conditions = ["t.user_id = %s"]
    params = [user_id]

    if start_date and end_date:
        conditions.append("t.transaction_date BETWEEN %s AND %s")
        params.extend([start_date, end_date])
    elif year and month:
        conditions.append("YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s")
        params.extend([year, month])
    elif year:
        conditions.append("YEAR(t.transaction_date) = %s")
        params.append(year)

    sql = f"""
        SELECT 
            t.transaction_id,
            t.user_id,
            t.category_id,
            c.category_name,
            c.category_type,
            c.color,
            c.icon,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description,
            t.created_at
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE {" AND ".join(conditions)}
        ORDER BY t.transaction_date DESC, t.transaction_id DESC;
    """

    rows = query_db(sql, tuple(params))
    
    if not rows:
        # Return empty DataFrame with defined schema
        return pd.DataFrame(columns=[
            'transaction_id', 'user_id', 'category_id', 'category_name', 
            'category_type', 'color', 'icon', 'transaction_type', 
            'amount', 'transaction_date', 'description', 'created_at'
        ])

    df = pd.DataFrame(rows)
    # Ensure amount is float for NumPy calculations and JSON serialization
    df['amount'] = df['amount'].astype(float)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    return df


def get_category_expense_breakdown(user_id, year=None, month=None, start_date=None, end_date=None):
    """
    Aggregates expense transactions by category.
    Returns category labels, amounts, counts, percentages, and colors for Chart.js and reports.
    """
    df = get_user_transactions_df(user_id, start_date=start_date, end_date=end_date, year=year, month=month)
    
    if df.empty:
        return {
            'labels': [],
            'data': [],
            'percentages': [],
            'colors': [],
            'icons': [],
            'counts': [],
            'total_expense': 0.0,
            'has_data': False
        }

    # Filter for expenses only
    expense_df = df[df['transaction_type'] == 'expense']
    if expense_df.empty:
        return {
            'labels': [],
            'data': [],
            'percentages': [],
            'colors': [],
            'icons': [],
            'counts': [],
            'total_expense': 0.0,
            'has_data': False
        }

    # Group by category attributes
    grouped = expense_df.groupby(
        ['category_id', 'category_name', 'color', 'icon'], 
        as_index=False
    ).agg(
        total_amount=('amount', 'sum'),
        txn_count=('transaction_id', 'count')
    ).sort_values(by='total_amount', ascending=False)

    total_expense = float(grouped['total_amount'].sum())
    
    # Calculate percentage safely using NumPy (avoid divide-by-zero)
    if total_expense > 0:
        grouped['percentage'] = np.round((grouped['total_amount'] / total_expense) * 100.0, 1)
    else:
        grouped['percentage'] = 0.0

    labels = grouped['category_name'].tolist()
    data = [float(x) for x in grouped['total_amount'].tolist()]
    percentages = [float(x) for x in grouped['percentage'].tolist()]
    colors = grouped['color'].tolist()
    icons = grouped['icon'].tolist()
    counts = [int(x) for x in grouped['txn_count'].tolist()]

    return {
        'labels': labels,
        'data': data,
        'percentages': percentages,
        'colors': colors,
        'icons': icons,
        'counts': counts,
        'total_expense': total_expense,
        'has_data': True
    }


def get_monthly_income_expense_summary(user_id, year):
    """
    Aggregates income vs. expense vs. savings for all 12 months of the given year.
    Returns month names, income array, expense array, savings array, and savings rates.
    """
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    df = get_user_transactions_df(user_id, year=year)

    incomes = np.zeros(12, dtype=float)
    expenses = np.zeros(12, dtype=float)
    counts = np.zeros(12, dtype=int)

    if not df.empty:
        df['month'] = df['transaction_date'].dt.month
        for m in range(1, 13):
            m_df = df[df['month'] == m]
            if not m_df.empty:
                inc = m_df[m_df['transaction_type'] == 'income']['amount'].sum()
                exp = m_df[m_df['transaction_type'] == 'expense']['amount'].sum()
                incomes[m - 1] = float(inc)
                expenses[m - 1] = float(exp)
                counts[m - 1] = int(len(m_df))

    # Calculate net savings = income - expense
    savings = incomes - expenses

    # Calculate savings rate: (savings / income) * 100
    # Safe NumPy division handling divide-by-zero
    savings_rate = np.zeros(12, dtype=float)
    for i in range(12):
        if incomes[i] > 0:
            savings_rate[i] = round(float((savings[i] / incomes[i]) * 100.0), 1)
        elif expenses[i] > 0:
            savings_rate[i] = -100.0
        else:
            savings_rate[i] = 0.0

    total_income = float(np.sum(incomes))
    total_expense = float(np.sum(expenses))
    total_savings = float(np.sum(savings))
    overall_savings_rate = round(float((total_savings / total_income) * 100.0), 1) if total_income > 0 else 0.0

    has_data = bool(total_income > 0 or total_expense > 0)

    # Monthly breakdown objects for reports table
    monthly_rows = []
    for i in range(12):
        monthly_rows.append({
            'month_number': i + 1,
            'month_name': month_names[i],
            'income': float(incomes[i]),
            'expense': float(expenses[i]),
            'savings': float(savings[i]),
            'savings_rate': float(savings_rate[i]),
            'transaction_count': int(counts[i])
        })

    return {
        'months': month_names,
        'incomes': [float(x) for x in incomes],
        'expenses': [float(x) for x in expenses],
        'savings': [float(x) for x in savings],
        'savings_rate': [float(x) for x in savings_rate],
        'total_income': total_income,
        'total_expense': total_expense,
        'total_savings': total_savings,
        'overall_savings_rate': overall_savings_rate,
        'monthly_rows': monthly_rows,
        'has_data': has_data
    }


def get_daily_totals(user_id, start_date, end_date):
    """
    Computes daily totals for income, expense, and net savings within a specified date range.
    Returns list of dicts for tabular reporting and charts.
    """
    df = get_user_transactions_df(user_id, start_date=start_date, end_date=end_date)
    
    if df.empty:
        return {
            'rows': [],
            'dates': [],
            'income': [],
            'expense': [],
            'savings': [],
            'total_income': 0.0,
            'total_expense': 0.0,
            'net_savings': 0.0,
            'has_data': False
        }

    df['date_str'] = df['transaction_date'].dt.strftime('%Y-%m-%d')

    # Group by date and transaction type
    grouped = df.groupby(['date_str', 'transaction_type'])['amount'].sum().unstack(fill_value=0.0)
    
    if 'income' not in grouped.columns:
        grouped['income'] = 0.0
    if 'expense' not in grouped.columns:
        grouped['expense'] = 0.0

    grouped['savings'] = grouped['income'] - grouped['expense']

    # Transaction count per date
    counts = df.groupby('date_str')['transaction_id'].count()
    grouped['txn_count'] = counts

    # Sort descending for reports table
    sorted_df = grouped.sort_index(ascending=False).reset_index()

    rows = []
    for _, r in sorted_df.iterrows():
        rows.append({
            'date': r['date_str'],
            'income': float(r['income']),
            'expense': float(r['expense']),
            'savings': float(r['savings']),
            'count': int(r['txn_count'])
        })

    total_income = float(df[df['transaction_type'] == 'income']['amount'].sum())
    total_expense = float(df[df['transaction_type'] == 'expense']['amount'].sum())
    net_savings = total_income - total_expense

    # Sort ascending for chronological charts
    chronological = grouped.sort_index(ascending=True)

    return {
        'rows': rows,
        'dates': chronological.index.tolist(),
        'income': [float(x) for x in chronological['income']],
        'expense': [float(x) for x in chronological['expense']],
        'savings': [float(x) for x in chronological['savings']],
        'total_income': total_income,
        'total_expense': total_expense,
        'net_savings': net_savings,
        'has_data': True
    }


def get_savings_trend(user_id, year=None):
    """
    Computes monthly savings and cumulative savings progression for a given year.
    Returns labels and data points for a smooth trend line chart.
    """
    summary = get_monthly_income_expense_summary(user_id, year=year or date.today().year)
    
    savings = summary['savings']
    cumulative_savings = np.cumsum(savings)

    return {
        'labels': summary['months'],
        'monthly_savings': [float(x) for x in savings],
        'cumulative_savings': [float(x) for x in cumulative_savings],
        'savings_rate': summary['savings_rate'],
        'has_data': summary['has_data']
    }


def get_budget_utilization_analytics(user_id, year, month):
    """
    Calculates budget utilization comparing monthly spending vs. limits per expense category.
    Returns formatted lists for horizontal bar chart and status tags.
    """
    # 1. Fetch configured limits
    limits_sql = """
        SELECT 
            c.category_id,
            c.category_name,
            c.color,
            c.icon,
            COALESCE(b.budget_amount, 0.00) AS budget_limit
        FROM categories c
        LEFT JOIN monthly_budgets b ON c.category_id = b.category_id 
             AND b.user_id = %s AND b.budget_year = %s AND b.budget_month = %s
        WHERE c.category_type = 'expense'
        ORDER BY c.category_name ASC;
    """
    categories = query_db(limits_sql, (user_id, year, month))
    
    # 2. Fetch actual spending
    spending_sql = """
        SELECT 
            category_id,
            COALESCE(SUM(amount), 0.00) AS total_spent
        FROM transactions
        WHERE user_id = %s 
          AND transaction_type = 'expense'
          AND YEAR(transaction_date) = %s 
          AND MONTH(transaction_date) = %s
        GROUP BY category_id;
    """
    spending_rows = query_db(spending_sql, (user_id, year, month))
    spending_map = {r['category_id']: float(r['total_spent']) for r in spending_rows}

    labels = []
    budgets = []
    spents = []
    percentages = []
    colors = []
    statuses = []
    items = []

    has_limits = False

    for cat in categories:
        cat_id = cat['category_id']
        limit = float(cat['budget_limit'])
        spent = spending_map.get(cat_id, 0.0)

        if limit > 0:
            has_limits = True
            pct = round((spent / limit) * 100.0, 1)
            if pct >= 100.0:
                status = 'exceeded'
            elif pct >= 80.0:
                status = 'warning'
            else:
                status = 'safe'
        else:
            pct = 0.0
            status = 'no_limit'

        labels.append(cat['category_name'])
        budgets.append(limit)
        spents.append(spent)
        percentages.append(pct)
        colors.append(cat['color'])
        statuses.append(status)

        items.append({
            'category_id': cat_id,
            'category_name': cat['category_name'],
            'color': cat['color'],
            'icon': cat['icon'],
            'limit': limit,
            'spent': spent,
            'remaining': max(0.0, limit - spent),
            'percentage': pct,
            'status': status
        })

    return {
        'labels': labels,
        'budgets': budgets,
        'spents': spents,
        'percentages': percentages,
        'colors': colors,
        'statuses': statuses,
        'items': items,
        'has_limits': has_limits,
        'has_data': bool(sum(spents) > 0 or has_limits)
    }


def get_month_over_month_comparison(user_id, year, month):
    """
    Compares the selected month's expenses, income, and savings with the prior calendar month.
    """
    # Current month
    curr_df = get_user_transactions_df(user_id, year=year, month=month)
    curr_inc = float(curr_df[curr_df['transaction_type'] == 'income']['amount'].sum()) if not curr_df.empty else 0.0
    curr_exp = float(curr_df[curr_df['transaction_type'] == 'expense']['amount'].sum()) if not curr_df.empty else 0.0
    curr_sav = curr_inc - curr_exp

    # Prior month
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    prev_df = get_user_transactions_df(user_id, year=prev_year, month=prev_month)
    prev_inc = float(prev_df[prev_df['transaction_type'] == 'income']['amount'].sum()) if not prev_df.empty else 0.0
    prev_exp = float(prev_df[prev_df['transaction_type'] == 'expense']['amount'].sum()) if not prev_df.empty else 0.0
    prev_sav = prev_inc - prev_exp

    # Spending difference and percent change
    exp_diff = curr_exp - prev_exp
    if prev_exp > 0:
        exp_pct_change = round(((curr_exp - prev_exp) / prev_exp) * 100.0, 1)
    elif curr_exp > 0:
        exp_pct_change = 100.0
    else:
        exp_pct_change = 0.0

    # Income difference and percent change
    inc_diff = curr_inc - prev_inc
    if prev_inc > 0:
        inc_pct_change = round(((curr_inc - prev_inc) / prev_inc) * 100.0, 1)
    elif curr_inc > 0:
        inc_pct_change = 100.0
    else:
        inc_pct_change = 0.0

    return {
        'current': {'income': curr_inc, 'expense': curr_exp, 'savings': curr_sav},
        'previous': {'income': prev_inc, 'expense': prev_exp, 'savings': prev_sav},
        'expense_diff': exp_diff,
        'expense_pct_change': exp_pct_change,
        'income_diff': inc_diff,
        'income_pct_change': inc_pct_change,
        'spent_more': exp_diff > 0,
        'spent_less': exp_diff < 0
    }


def get_analytics_insights(user_id, year=None, month=None):
    """
    Generates intelligent textual insights for the user based on spending patterns,
    month-over-month differences, and budget utilization.
    """
    today = date.today()
    y = year or today.year
    m = month or today.month

    # 1. Category breakdown
    cat_data = get_category_expense_breakdown(user_id, year=y, month=m)
    
    # 2. Month-over-month
    mom = get_month_over_month_comparison(user_id, y, m)

    # 3. Monthly summary
    monthly = get_monthly_income_expense_summary(user_id, y)
    curr_month_row = next((r for r in monthly['monthly_rows'] if r['month_number'] == m), None)

    insights = []

    # Insight 1: Highest spending category
    if cat_data['has_data'] and len(cat_data['labels']) > 0:
        top_cat = cat_data['labels'][0]
        top_amt = cat_data['data'][0]
        top_pct = cat_data['percentages'][0]
        insights.append({
            'type': 'top_category',
            'title': 'Highest Spending Category',
            'text': f"Highest spending category this month: {top_cat} (₹{top_amt:,.2f}, {top_pct}% of total expenses)",
            'icon': 'bi-trophy',
            'color': 'primary'
        })
    else:
        insights.append({
            'type': 'top_category',
            'title': 'Highest Spending Category',
            'text': "No expenses recorded for this month yet.",
            'icon': 'bi-info-circle',
            'color': 'secondary'
        })

    # Insight 2: Month-over-month spending trend
    if mom['previous']['expense'] > 0:
        abs_pct = abs(mom['expense_pct_change'])
        if mom['spent_more']:
            msg = f"You spent {abs_pct}% more than last month (+₹{abs(mom['expense_diff']):,.2f})."
            color = 'danger'
            icon = 'bi-arrow-up-right'
        elif mom['spent_less']:
            msg = f"You spent {abs_pct}% less than last month (-₹{abs(mom['expense_diff']):,.2f}). Great job!"
            color = 'success'
            icon = 'bi-arrow-down-right'
        else:
            msg = "Your spending is exactly identical to last month."
            color = 'info'
            icon = 'bi-arrow-right'
    else:
        if mom['current']['expense'] > 0:
            msg = f"Total spending this month is ₹{mom['current']['expense']:,.2f} (no expenses recorded last month)."
        else:
            msg = "No prior spending data to compare."
        color = 'secondary'
        icon = 'bi-calendar-event'

    insights.append({
        'type': 'month_over_month',
        'title': 'Monthly Spending Change',
        'text': msg,
        'icon': icon,
        'color': color
    })

    # Insight 3: Savings rate
    if curr_month_row and curr_month_row['income'] > 0:
        rate = curr_month_row['savings_rate']
        if rate >= 30:
            badge_color = 'success'
            eval_msg = "Outstanding savings performance!"
        elif rate >= 15:
            badge_color = 'primary'
            eval_msg = "Healthy savings rate."
        elif rate >= 0:
            badge_color = 'warning'
            eval_msg = "Moderate savings. Consider reducing non-essential expenses."
        else:
            badge_color = 'danger'
            eval_msg = "Spending exceeded income this month."

        insights.append({
            'type': 'savings_rate',
            'title': 'Savings Rate',
            'text': f"Current savings rate: {rate}% (₹{curr_month_row['savings']:,.2f} saved). {eval_msg}",
            'icon': 'bi-piggy-bank',
            'color': badge_color
        })
    elif curr_month_row and curr_month_row['expense'] > 0:
        insights.append({
            'type': 'savings_rate',
            'title': 'Savings Rate',
            'text': f"Expenses recorded without income this month (₹{curr_month_row['expense']:,.2f}).",
            'icon': 'bi-exclamation-triangle',
            'color': 'danger'
        })
    else:
        insights.append({
            'type': 'savings_rate',
            'title': 'Savings Rate',
            'text': "No income or expense records for this month.",
            'icon': 'bi-piggy-bank',
            'color': 'secondary'
        })

    return {
        'insights': insights,
        'month_over_month': mom,
        'category_data': cat_data,
        'month_summary': curr_month_row
    }


def get_spending_status(income, expenses):
    """
    Evaluates monthly spending relative to income:
    - safe: expenses <= 50% of income (no banner, normal cards)
    - warning: expenses > 50% and <= 100% of income (amber banner, amber card)
    - danger: expenses > income (red banner, red cards)
    - no_income: income <= 0 (no banner, no error)
    
    Returns a dictionary with status, percentage, capped percentage, and over amount.
    """
    from decimal import Decimal
    try:
        inc = Decimal(str(income or 0))
    except Exception:
        inc = Decimal('0.00')

    try:
        exp = Decimal(str(expenses or 0))
    except Exception:
        exp = Decimal('0.00')

    if inc <= Decimal('0'):
        status = 'no_income'
        pct = 0.0
        over = Decimal('0.00')
    else:
        pct = float((exp / inc) * 100)
        if exp > inc:
            status = 'danger'
            over = exp - inc
        elif exp > (inc * Decimal('0.5')):
            status = 'warning'
            over = Decimal('0.00')
        else:
            status = 'safe'
            over = Decimal('0.00')

    pct_rounded = round(pct, 1)
    capped_pct = min(pct_rounded, 100.0)

    return {
        'status': status,
        'percentage': pct_rounded,
        'capped_percentage': capped_pct,
        'over_amount': over,
        'income': inc,
        'expenses': exp
    }

