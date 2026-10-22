# Capstone Submission Screenshots Checklist

This checklist details every screenshot required for your formal college project report and final presentation. Follow the instructions for each item to capture the exact page state.

---

## Screenshot Matrix

| # | Filename Suggestion | Page / Route | Viewport | Required State & Elements to Highlight |
|:---|:---|:---|:---:|:---|
| **01** | `01_landing_page.png` | Public Home (`/`) | Desktop (1280px) | Clean hero section showing "Take Control of Your Household Finances", Feature Highlights, and Login/Register buttons. |
| **02** | `02_user_login.png` | Login (`/auth/login`) | Desktop (1280px) | Centered login card prefilled with demo credentials banner (`demo@example.com` / `Demo@1234`). |
| **03** | `03_dashboard_overview.png` | Dashboard (`/dashboard`) | Desktop (1280px) | Full view showing Month Selector (October 2026), 4 Summary Metric Cards, Top Spending Categories, and Recent Transactions. |
| **04** | `04_overspending_alert.png` | Dashboard (`/dashboard`) | Desktop (1280px) | Red/Amber **Overspending Alert Banner** showing categories exceeding or nearing limits (e.g. Groceries exceeded by ₹500). |
| **05** | `05_transactions_desktop.png` | Transactions (`/transactions`) | Desktop (1280px) | Full transaction history table with active filters, colored category badges, sorting arrows on columns, and pagination at the bottom. |
| **06** | `06_transactions_filter.png` | Transactions (`/transactions`) | Desktop (1280px) | Filter bar populated with Date Range + Type: Expense + Category: Groceries showing matching filtered results count. |
| **07** | `07_transaction_edit_modal.png` | Edit (`/transactions/<id>/edit`) | Desktop (1280px) | Edit transaction form prefilled with existing amount, date, category, and description. |
| **08** | `08_delete_modal.png` | Transactions (`/transactions`) | Desktop (1280px) | Interactive Bootstrap Delete Confirmation Modal open, displaying the exact transaction note, formatted currency amount, and Delete button. |
| **09** | `09_monthly_budgets.png` | Budgets (`/budgets`) | Desktop (1280px) | Monthly Budgets table showing categories, current spending, limit input fields, progress bars (green/amber/red), and "Save All" button. |
| **10** | `10_yearly_budget_summary.png` | Yearly Budgets (`/budgets/yearly`) | Desktop (1280px) | 12-month annual overview table comparing monthly limits vs. actual spent and category yearly cards. |
| **11** | `11_interactive_analysis.png` | Analysis (`/reports/analysis`) | Desktop (1280px) | All 4 Chart.js charts: Category Doughnut, Monthly Income vs Expense Bar, Savings Trend Line, and Budget Utilization Bar. |
| **12** | `12_reports_datewise.png` | Reports (`/reports?tab=datewise`) | Desktop (1280px) | Date-wise report tab showing custom date range filter, summary metric cards, daily table, and "Export CSV" button. |
| **13** | `13_reports_category.png` | Reports (`/reports?tab=category`) | Desktop (1280px) | Category-wise tab showing embedded Matplotlib PNG chart preview alongside the category distribution table. |
| **14** | `14_reports_monthly.png` | Reports (`/reports?tab=monthly`) | Desktop (1280px) | 12-Month Annual Report showing server-generated Matplotlib grouped bar chart and 12-month performance table. |
| **15** | `15_print_preview.png` | Reports Print Mode | Desktop (1280px) | Browser print preview dialog (`Ctrl + P`) on `/reports` showing clean printable financial statement with no sidebars or buttons. |
| **16** | `16_mobile_stacked_cards.png` | Transactions (`/transactions`) | Mobile (375px) | Mobile responsive view showing transactions rendered as stacked cards with 44px touch action buttons. |
| **17** | `17_dark_mode.png` | Dashboard (`/dashboard`) | Desktop (1280px) | Dark mode theme activated via topbar toggle button showing deep slate background (`#0f172a`) and high-contrast text. |
| **18** | `18_custom_403_404.png` | Error View (`/nonexistent`) | Desktop (1280px) | Branded 404 or 403 error page with custom wallet shield graphic and "Return to Dashboard" action. |
| **19** | `19_pytest_terminal.png` | Terminal / PowerShell | Terminal Window | PowerShell window showing `pytest -v tests/` output with **30 passed in X.XXs (100%)**. |

---

## Tips for High-Quality Captures
1. Use **Light Mode** for screenshots #01 through #16 to ensure high-contrast readability in your printed college report.
2. Capture screenshot #17 specifically to demonstrate the **Dark Mode** feature.
3. For mobile screenshots, press `F12` in Chrome/Edge, toggle Device Mode (`Ctrl + Shift + M`), select **iPhone SE** or **iPhone 12 Pro (375px - 390px)**, and take a screenshot.
4. Save screenshots in a `docs/screenshots/` folder for easy inclusion in your Word or LaTeX project report.
