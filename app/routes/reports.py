"""
Reports and Analysis routes.
Provides interactive tabbed reports (Date-wise, Category-wise, Monthly),
Matplotlib static chart previews, CSV export streams generated via Pandas,
and the dedicated Financial Analysis visual dashboard.
"""
import io
from datetime import date, timedelta
from flask import (
    Blueprint, render_template, request, Response, 
    send_file, abort, current_app
)
import pandas as pd
from app.auth.decorators import login_required
from app.utils import get_current_user_id, format_currency
from app.services.analytics import (
    get_user_transactions_df,
    get_category_expense_breakdown,
    get_monthly_income_expense_summary,
    get_daily_totals,
    get_budget_utilization_analytics,
    get_analytics_insights
)
from app.services.charts import (
    generate_expense_pie_chart,
    generate_monthly_bar_chart,
    generate_budget_horizontal_bar_chart
)
from app.services.queries import get_distinct_transaction_years

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('', strict_slashes=False)
@reports_bp.route('/', strict_slashes=False)
@login_required
def reports_index():
    """
    Financial Reports hub with 3 responsive tabs:
    1. Date-wise Daily Summary
    2. Category-wise Spending Breakdown
    3. 12-Month Annual Summary
    """
    user_id = get_current_user_id()
    today = date.today()

    active_tab = request.args.get('tab', 'datewise')
    
    # Date-wise parameters (default: past 30 days)
    start_date = request.args.get('start_date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))

    # Category and Monthly parameters
    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    # Available years for filter dropdown
    available_years = get_distinct_transaction_years(user_id)
    if today.year not in available_years:
        available_years.insert(0, today.year)

    # 1. Date-wise report data
    daily_data = get_daily_totals(user_id, start_date=start_date, end_date=end_date)

    # 2. Category-wise report data
    category_data = get_category_expense_breakdown(user_id, year=year, month=month)
    _, cat_chart_b64 = generate_expense_pie_chart(category_data)

    # 3. Monthly 12-month report data
    monthly_data = get_monthly_income_expense_summary(user_id, year=year)
    _, monthly_chart_b64 = generate_monthly_bar_chart(monthly_data)

    # 4. Budget utilization
    budget_data = get_budget_utilization_analytics(user_id, year=year, month=month)
    _, budget_chart_b64 = generate_budget_horizontal_bar_chart(budget_data)

    return render_template(
        'reports/index.html',
        active_tab=active_tab,
        start_date=start_date,
        end_date=end_date,
        selected_year=year,
        selected_month=month,
        available_years=available_years,
        daily_data=daily_data,
        category_data=category_data,
        monthly_data=monthly_data,
        budget_data=budget_data,
        cat_chart_b64=cat_chart_b64,
        monthly_chart_b64=monthly_chart_b64,
        budget_chart_b64=budget_chart_b64,
        today=today
    )


@reports_bp.route('/analysis', strict_slashes=False)
@login_required
def analysis_page():
    """
    Dedicated Interactive Financial Analysis Page with Chart.js visualizations
    and textual financial health insights.
    """
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    available_years = get_distinct_transaction_years(user_id)
    if today.year not in available_years:
        available_years.insert(0, today.year)

    insights_data = get_analytics_insights(user_id, year=year, month=month)

    return render_template(
        'reports/analysis.html',
        selected_year=year,
        selected_month=month,
        available_years=available_years,
        insights_data=insights_data,
        today=today
    )


@reports_bp.route('/charts/<chart_type>.png')
@login_required
def serve_matplotlib_chart(chart_type):
    """
    Serves a dynamically rendered Matplotlib PNG image for direct viewing or embedding.
    """
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    if chart_type == 'expense-distribution':
        data = get_category_expense_breakdown(user_id, year=year, month=month)
        img_bytes, _ = generate_expense_pie_chart(data)
    elif chart_type == 'monthly-summary':
        data = get_monthly_income_expense_summary(user_id, year=year)
        img_bytes, _ = generate_monthly_bar_chart(data)
    elif chart_type == 'budget-utilization':
        data = get_budget_utilization_analytics(user_id, year=year, month=month)
        img_bytes, _ = generate_budget_horizontal_bar_chart(data)
    else:
        abort(404)

    return Response(img_bytes, mimetype='image/png')


@reports_bp.route('/export/daily')
@login_required
def export_daily_csv():
    """Exports date-wise daily totals report as a CSV file using Pandas."""
    user_id = get_current_user_id()
    today = date.today()

    start_date = request.args.get('start_date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))

    daily_data = get_daily_totals(user_id, start_date=start_date, end_date=end_date)
    
    if daily_data['rows']:
        df = pd.DataFrame(daily_data['rows'])
        df.rename(columns={
            'date': 'Date',
            'income': 'Income (INR)',
            'expense': 'Expense (INR)',
            'savings': 'Net Savings (INR)',
            'count': 'Transaction Count'
        }, inplace=True)
    else:
        df = pd.DataFrame(columns=['Date', 'Income (INR)', 'Expense (INR)', 'Net Savings (INR)', 'Transaction Count'])

    out = io.StringIO()
    df.to_csv(out, index=False)
    
    filename = f"daily_report_{start_date}_to_{end_date}.csv"
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@reports_bp.route('/export/category')
@login_required
def export_category_csv():
    """Exports category-wise spending report as a CSV file using Pandas."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    cat_data = get_category_expense_breakdown(user_id, year=year, month=month)
    
    if cat_data['has_data']:
        df = pd.DataFrame({
            'Category': cat_data['labels'],
            'Total Amount (INR)': cat_data['data'],
            'Percentage (%)': cat_data['percentages'],
            'Transactions Count': cat_data['counts']
        })
    else:
        df = pd.DataFrame(columns=['Category', 'Total Amount (INR)', 'Percentage (%)', 'Transactions Count'])

    out = io.StringIO()
    df.to_csv(out, index=False)
    
    filename = f"category_report_{year}_{month:02d}.csv"
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@reports_bp.route('/export/monthly')
@login_required
def export_monthly_csv():
    """Exports 12-month annual summary report as a CSV file using Pandas."""
    user_id = get_current_user_id()
    today = date.today()

    try:
        year = int(request.args.get('year', today.year))
    except (ValueError, TypeError):
        year = today.year

    monthly_data = get_monthly_income_expense_summary(user_id, year=year)
    
    rows = []
    for r in monthly_data['monthly_rows']:
        rows.append({
            'Month': r['month_name'],
            'Income (INR)': r['income'],
            'Expense (INR)': r['expense'],
            'Net Savings (INR)': r['savings'],
            'Savings Rate (%)': r['savings_rate'],
            'Transaction Count': r['transaction_count']
        })

    df = pd.DataFrame(rows)
    out = io.StringIO()
    df.to_csv(out, index=False)
    
    filename = f"monthly_summary_{year}.csv"
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
