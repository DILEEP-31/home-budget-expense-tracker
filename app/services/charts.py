"""
Matplotlib chart generation service.
Uses the headless 'Agg' backend to safely render high-resolution PNG charts on the server.
Guarantees clean figure closure (plt.close) in finally blocks to prevent memory leaks.
"""
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _fig_to_base64_and_bytes(fig):
    """
    Helper to convert a matplotlib figure into raw PNG bytes and a base64 data URI string.
    Ensures plt.close(fig) is invoked.
    """
    try:
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=False, facecolor='#ffffff')
        buf.seek(0)
        img_bytes = buf.getvalue()
        base64_str = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
        return img_bytes, base64_str
    finally:
        plt.close(fig)


def generate_expense_pie_chart(category_data):
    """
    Generates an expense distribution doughnut/pie chart.
    Returns (raw_bytes, base64_uri).
    """
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    
    if not category_data or not category_data.get('has_data') or not category_data.get('data'):
        ax.text(0.5, 0.5, "No Expense Data Available", 
                horizontalalignment='center', verticalalignment='center',
                fontsize=13, color='#6b7280', transform=ax.transAxes)
        ax.axis('off')
        return _fig_to_base64_and_bytes(fig)

    labels = category_data['labels']
    data = category_data['data']
    colors = category_data['colors']

    # Doughnut chart
    wedges, texts, autotexts = ax.pie(
        data, 
        labels=labels, 
        colors=colors, 
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2)
    )

    # Style percentage text
    for autotext in autotexts:
        autotext.set_color('#1f2937')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')

    for text in texts:
        text.set_fontsize(9)
        text.set_color('#374151')

    ax.set_title("Expense Distribution by Category", fontsize=12, fontweight='bold', pad=15, color='#111827')
    return _fig_to_base64_and_bytes(fig)


def generate_monthly_bar_chart(monthly_summary):
    """
    Generates a grouped bar chart comparing Income vs Expense for each month of the year.
    Returns (raw_bytes, base64_uri).
    """
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
    
    if not monthly_summary or not monthly_summary.get('has_data'):
        ax.text(0.5, 0.5, "No Transaction Data for this Year", 
                horizontalalignment='center', verticalalignment='center',
                fontsize=13, color='#6b7280', transform=ax.transAxes)
        ax.axis('off')
        return _fig_to_base64_and_bytes(fig)

    months = monthly_summary['months']
    incomes = monthly_summary['incomes']
    expenses = monthly_summary['expenses']

    x = np.arange(len(months))
    width = 0.35

    rects1 = ax.bar(x - width/2, incomes, width, label='Income', color='#10b981', edgecolor='none', alpha=0.9, zorder=3)
    rects2 = ax.bar(x + width/2, expenses, width, label='Expense', color='#ef4444', edgecolor='none', alpha=0.9, zorder=3)

    ax.set_ylabel('Amount (₹)', fontsize=10, fontweight='medium', color='#374151')
    ax.set_title('Monthly Income vs Expense', fontsize=12, fontweight='bold', pad=15, color='#111827')
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=9, color='#4b5563')
    ax.legend(frameon=False, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.3, zorder=0)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#d1d5db')
    ax.spines['bottom'].set_color('#d1d5db')

    return _fig_to_base64_and_bytes(fig)


def generate_budget_horizontal_bar_chart(budget_utilization):
    """
    Generates a horizontal grouped/stacked bar chart for Category Budget Utilization (Budget vs Spent).
    Returns (raw_bytes, base64_uri).
    """
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

    if not budget_utilization or not budget_utilization.get('has_data') or not budget_utilization.get('labels'):
        ax.text(0.5, 0.5, "No Budget Limits Configured", 
                horizontalalignment='center', verticalalignment='center',
                fontsize=13, color='#6b7280', transform=ax.transAxes)
        ax.axis('off')
        return _fig_to_base64_and_bytes(fig)

    labels = budget_utilization['labels']
    budgets = budget_utilization['budgets']
    spents = budget_utilization['spents']

    y = np.arange(len(labels))
    height = 0.35

    ax.barh(y - height/2, budgets, height, label='Budget Limit', color='#93c5fd', alpha=0.85, zorder=3)
    ax.barh(y + height/2, spents, height, label='Actual Spent', color='#f87171', alpha=0.9, zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9, color='#374151')
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Amount (₹)', fontsize=10, color='#374151')
    ax.set_title('Budget Limit vs. Actual Spending', fontsize=12, fontweight='bold', pad=15, color='#111827')
    ax.legend(frameon=False, loc='lower right')
    ax.grid(axis='x', linestyle='--', alpha=0.3, zorder=0)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#d1d5db')
    ax.spines['bottom'].set_color('#d1d5db')

    return _fig_to_base64_and_bytes(fig)
