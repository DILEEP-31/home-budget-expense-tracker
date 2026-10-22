# Home Budget — Expense Tracker & Financial Analysis System

A full-stack Python web application designed for personal finance tracking, budget enforcement, data analytics, and reporting. Built with Flask 3, MySQL 8, Pandas, NumPy, Matplotlib, Chart.js, and Bootstrap 5.

---

## 1. Project Overview
**Home Budget** is a full-stack college capstone project that enables users to track income and expenditures, set category-wise monthly and annual budgets with automated overspending alerts, explore visual spending trends through interactive and server-generated charts, and export custom financial statements to CSV.

---

## 2. Key Features
- **User Authentication & Authorization:**
  - Secure user registration with validation (password minimum 8 characters with at least one letter and one number).
  - Password hashing via Werkzeug (Scrypt/PBKDF2); plaintext passwords are never logged or stored.
  - Session hardening with `HttpOnly` and `SameSite=Lax`.
  - Object-level ownership verification: Cross-user access attempts strictly return HTTP 404.
  - CSRF protection across all state-altering POST forms.
- **Transaction Management (CRUD):**
  - Add, edit, and delete transactions (income and expense) with category validation.
  - Multi-criteria filter bar: Date range, transaction type, category, and minimum/maximum amount.
  - Parameterized full-text search with wildcard escaping (`%` and `_`) to prevent SQL injection.
  - Whitelist-enforced sorting by date, amount, category, and type (ASC/DESC).
  - Responsive pagination (10 records/page) preserving active filters in URL queries.
  - Responsive mobile design: Renders wide tables on desktop and stacked cards under 768px.
- **Budgets & Overspending Alerts:**
  - Monthly budget manager allowing batch updates using `INSERT ... ON DUPLICATE KEY UPDATE`.
  - Status thresholds: Safe (<80%), Warning (80%–99.9%), and Exceeded ($\ge$100%).
  - Quick propagation tools: "Copy from previous month" and "Apply to all months of this year".
  - Overspending alert banners on both the Dashboard and Budgets views.
  - 12-month annual budget matrix.
- **Data Analytics & Visualizations:**
  - Statistical aggregation engine built with Pandas and NumPy.
  - 4 Interactive Chart.js charts: Category Expense Doughnut, Monthly Income vs. Expense Grouped Bar, Savings Trend Line, and Budget Utilization Horizontal Bar.
  - Textual financial insights: Top spending category, month-over-month variance %, and savings rate.
  - Headless Matplotlib (`Agg`) generating high-resolution PNG charts with clean memory management (`plt.close()`).
- **Reports & Exporting:**
  - Three-tab financial statement: Date-wise daily totals, Category-wise breakdown, and 12-month annual summary.
  - Single-click CSV export streams generated via Pandas `to_csv`.
  - Print-friendly layout (`@media print`) hiding navigation chrome and formatting printable statements.
- **User Experience & Accessibility:**
  - Double-submit prevention with loading button spinners.
  - Auto-dismissing toast notifications (4s delay).
  - Client-side Dark Mode toggle storing preferences in browser `localStorage`.
  - Branded HTTP 400, 403, 404, and 500 error pages.

---

## 3. Technology Stack
- **Backend:** Python 3.11+, Flask 3.1.3, Jinja2, Flask-WTF (CSRF), Werkzeug.
- **Database:** MySQL 8 via PyMySQL (DictCursor) with connection pooling and parameterization.
- **Analytics & Charts:** Pandas 3.0+, NumPy 2.5+, Matplotlib 3.11+ (`Agg`), Chart.js 4.4+.
- **Frontend:** Bootstrap 5.3.3, Bootstrap Icons 1.11, Custom CSS/JS.
- **Testing:** pytest 9.1+.

---

## 4. Folder Structure
```text
home-budget-tracker/
├── app/
│   ├── __init__.py               # Flask app factory, blueprints, Jinja filters
│   ├── config.py                 # Configuration loader from .env
│   ├── db.py                     # Safe MySQL connection & query helpers
│   ├── utils.py                  # Server-side validators & formatting filters
│   ├── auth/                     # Authentication blueprint & decorators
│   │   ├── decorators.py         # @login_required decorator with 401 JSON API support
│   │   └── routes.py             # Login, register, logout routes
│   ├── routes/
│   │   ├── main.py               # Landing page, dashboard, transactions CRUD, CSV export
│   │   ├── budgets.py            # Monthly & yearly budget routes
│   │   ├── api.py                # Authenticated JSON endpoints for Chart.js
│   │   └── reports.py            # Reports hub, analysis page, CSV generators
│   ├── services/
│   │   ├── queries.py            # Parameterized SQL database queries
│   │   ├── budget_logic.py       # Pure budget status calculation & validation
│   │   ├── analytics.py          # Pandas & NumPy aggregations & insights
│   │   └── charts.py             # Matplotlib PNG chart generator (Agg)
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Main responsive layout wrapper
│   │   ├── home.html             # Public landing page
│   │   ├── dashboard.html        # Interactive financial dashboard
│   │   ├── auth/                 # Login & register forms
│   │   ├── transactions/         # Transaction list, new, edit, delete modal
│   │   ├── budgets/              # Monthly & yearly budget views
│   │   ├── reports/              # Tabbed reports & analysis dashboard
│   │   ├── errors/               # 400, 403, 404, 500 custom error views
│   │   └── partials/             # Topbar, sidebar, mobile offcanvas, toasts
│   └── static/
│       ├── css/style.css         # Fintech styles, dark mode, @media print
│       ├── js/app.js             # Button loading spinners, dark mode engine, toasts
│       ├── js/charts.js          # Chart.js asynchronous chart managers
│       └── img/favicon.svg       # Brand favicon
├── database/
│   ├── schema.sql                # Complete MySQL DDL schema
│   ├── init_db.py                # Database initialization script
│   ├── seed_sample_data.py       # Seed script (30+ transactions across 3 months)
│   └── create_demo_user.py       # Creates demo@example.com with hashed password
├── docs/
│   ├── PROJECT_DOCUMENTATION.md  # Comprehensive report for college submission
│   ├── TESTING.md                # Manual testing results & evidence
│   ├── SCREENSHOTS_CHECKLIST.md  # UI screenshots guide
│   └── DEMO_SCRIPT.md            # 5-7 minute presentation script & Q&A
├── tests/
│   ├── test_validation.py        # Validation unit tests
│   ├── test_auth_security.py     # Password hashing & security tests
│   ├── test_budget_logic.py      # Budget threshold tests (80% & 100% boundaries)
│   └── test_analytics.py         # Pandas/NumPy calculation tests
├── .env.example                  # Environment configuration template
├── requirements.txt              # Project Python dependencies
├── run.py                        # Application entry point
├── PROGRESS.md                   # Development milestone tracker
├── AGENT_RULES.md                # Capstone compliance guidelines
└── README.md                     # Project documentation
```

---

## 5. Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Python 3.11 or newer (Python 3.14 verified).
- **Database Server:** MySQL 8.0 Server running on port `3306`.
- **PowerShell:** Windows PowerShell 5.1+ or PowerShell Core.

---

## 6. Installation & Setup Instructions

### Step 1: Clone or Navigate to Project Directory
```powershell
cd c:\Users\dilee\OneDrive\Desktop\pyproject
```

### Step 2: Set Up Virtual Environment
```powershell
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` and verify database credentials:
```powershell
Copy-Item .env.example .env
```
Ensure your `.env` contains:
```ini
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=college-capstone-super-secret-key-2026-secure

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=home_budget_db

CURRENCY_SYMBOL=₹
```

### Step 5: Initialize MySQL Database & Seed Data
Execute the setup scripts in order:
```powershell
# 1. Initialize schema and default categories
python database/init_db.py

# 2. Seed initial multi-month transactions
python database/seed_sample_data.py

# 3. Create demo user with secure password hash
python database/create_demo_user.py
```

---

## 7. Demo User Credentials
A pre-configured demo account populated with transactions and budgets across August, September, October, and November 2026 is available for immediate testing:
- **Email:** `demo@example.com`
- **Password:** `Demo@1234`
*(Password hash is generated via `werkzeug.security.generate_password_hash` with Scrypt).*

---

## 8. Running the Application

### Option A: From PowerShell
```powershell
.\venv\Scripts\python.exe run.py
```
Open your browser and navigate to:
```text
http://localhost:5000
```

### Option B: Running in VS Code
1. Open the project folder in VS Code (`File -> Open Folder... -> pyproject`).
2. Select the Python interpreter: Press `Ctrl + Shift + P`, type `Python: Select Interpreter`, and choose `.\venv\Scripts\python.exe`.
3. Open `run.py` and press `F5` (or click **Run Without Debugging** `Ctrl + F5`).
4. Click the terminal link `http://127.0.0.1:5000` to open in your browser.

---

## 9. Running the Automated Test Suite
To run all 30 unit and integration tests using pytest:
```powershell
.\venv\Scripts\python.exe -m pytest -v tests/
```

To run a specific test module:
```powershell
.\venv\Scripts\python.exe -m pytest -v tests/test_budget_logic.py
```

---

## 10. Troubleshooting & Common Issues
1. **MySQL Connection Refused (`2003 / Can't connect`):**
   - Ensure the MySQL Windows service is running:
     ```powershell
     Get-Service *mysql* | Start-Service
     ```
   - Verify `DB_PORT=3306` and credentials in `.env`.
2. **PowerShell Script Execution Policy Error:**
   - If `Activate.ps1` is blocked, run:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
     ```
3. **Double-submit on slow connections:**
   - Client-side submit guard in `app.js` automatically disables buttons during submission.

---

## 11. Known Limitations
- Multi-currency conversion is not included; transactions use the primary system currency (`₹`).
- Recurring automated transactions (e.g. auto-debit on the 1st of every month) are not automated; transactions are recorded manually.
- Direct PDF generation relies on client-side browser print formatting (`window.print()`).
