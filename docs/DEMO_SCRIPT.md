# Project Demonstration Script & Trainer Q&A
## Home Budget (Expense Tracker and Analysis System)
**Target Presentation Time:** 5 to 7 Minutes

---

## Part 1: Step-by-Step Demonstration Walkthrough

### 1. Introduction (0:00 – 0:45)
- **What to Display:** Public Home Page (`http://localhost:5000/`) in Light Mode.
- **What to Say:**
  > "Good morning, respected trainer and evaluators. Today I am presenting **Home Budget**, a full-stack personal finance and expense tracking system built with Python, Flask, MySQL 8, Pandas, NumPy, Matplotlib, and Chart.js.
  > 
  > The primary objective of this project is to give households total control over their cash flows through real-time expense tracking, category budget enforcement with proactive alerts, and deep data analytics."

---

### 2. Authentication & Data Security (0:45 – 1:30)
- **What to Click:** Click **Log In** in the navbar.
- **What to Say:**
  > "First, we have secure multi-user authentication. Passwords are never stored or logged in plain text; instead, they are hashed using Werkzeug's Scrypt cryptographic algorithm.
  > 
  > Every form in the system is protected against Cross-Site Request Forgery (CSRF). I will log in using our pre-seeded demo user account: `demo@example.com`."
- **What to Click:** Enter `demo@example.com` and `Demo@1234`. Click **Sign In**.
- **What to Say:**
  > "Notice how the submit button immediately displays an animated loading spinner and disables itself. This prevents duplicate form submissions on slow connections."

---

### 3. Financial Dashboard & Overspending Alerts (1:30 – 2:45)
- **What to Display:** The Dashboard view (`/dashboard`).
- **What to Say:**
  > "Upon logging in, the user arrives at the Financial Dashboard. At the top, we have 4 summary metric cards: Monthly Income, Monthly Expenses, Monthly Net Savings with dynamic Savings Rate, and All-Time Net Balance. All these figures are computed live from MySQL using parameterized queries.
  > 
  > Right above the metrics, notice our **Overspending Alert Banner**. The system automatically scans active monthly budgets. If a category reaches 80% to 99% of its limit, an amber warning is triggered. If it reaches or exceeds 100%, a red alert appears specifying the exact amount over budget.
  > 
  > Below this, we also have interactive Chart.js charts: a Doughnut chart showing expense distribution and a grouped Bar chart comparing monthly income versus expenses."

---

### 4. Transactions Management (CRUD, Search & Filtering) (2:45 – 4:00)
- **What to Click:** Click **Transactions** in the sidebar.
- **What to Say:**
  > "Here is our full Transaction History ledger. Notice the features we built for large datasets:
  > 1. **Multi-criteria filtering:** We can filter by Date Range, Type (income or expense), Category, and Min/Max amounts.
  > 2. **Secure Search:** We can search descriptions. Special SQL characters like `%` and `_` are escaped to prevent injection.
  > 3. **Whitelist Sorting:** Columns like Date and Amount can be sorted in both ascending and descending order using a strict column whitelist.
  > 4. **Responsive Pagination:** We show 10 records per page, and our pagination links retain all active filter parameters in the URL."
- **What to Click:** Click the **Edit** icon on a transaction. Change the amount and save. Then click the **Delete** icon to show the confirmation modal.
- **What to Say:**
  > "Every transaction edit form reuses our server-side validation functions. Deletion requires explicit modal confirmation and verifies row-level ownership. If a user attempts to edit another user's record by tampering with the URL, the system returns a strict 404 response."

---

### 5. Budgets & Annual Budgeting (4:00 – 5:00)
- **What to Click:** Click **Budgets** in the sidebar.
- **What to Say:**
  > "Our Budgeting module allows users to configure monthly spending limits for every expense category.
  > 
  > Rather than submitting one category at a time, users can enter all limits and save them in a single batch request using an atomic MySQL `INSERT ... ON DUPLICATE KEY UPDATE` query.
  > 
  > We also built two productivity features: **'Copy from previous month'** to carry forward past limits, and **'Apply to all months of this year'** for yearly planning.
  > 
  > If we switch to the **Yearly Budget Summary** page, we see a full 12-month matrix comparing limits versus actual expenditures."

---

### 6. Analytics, Reports & CSV Exports (5:00 – 6:15)
- **What to Click:** Click **Analysis** in the sidebar.
- **What to Say:**
  > "Next is our Interactive Analysis page. We integrated Pandas and NumPy in `services/analytics.py` to aggregate user data into statistical DataFrames.
  > 
  > We have 4 dynamic Chart.js charts:
  > - An Expense Distribution Doughnut
  > - Monthly Income vs Expense Grouped Bar
  > - Savings Trend and Cumulative Growth Line
  > - Budget Utilization Horizontal Bar
  > 
  > Each chart features an asynchronous loading spinner, empty states, and custom currency tooltips. Above the charts, we generate smart textual insights such as our top spending category and month-over-month percentage changes."
- **What to Click:** Click **Reports** in the sidebar.
- **What to Say:**
  > "Finally, the **Reports** hub offers three tabs: Date-wise daily totals, Category-wise breakdown, and 12-Month annual summaries.
  > 
  > Notice the embedded charts: these are generated server-side using **Matplotlib's headless Agg backend**. We ensure `plt.close()` is always invoked to prevent memory leaks.
  > 
  > Users can export any report tab directly into a CSV spreadsheet generated via Pandas `to_csv`, or click **'Print / Save PDF'** which leverages our custom print stylesheet to format a clean financial statement."

---

### 7. Responsiveness, Dark Mode & Conclusion (6:15 – 7:00)
- **What to Click:** Click the **Dark Mode** toggle in the topbar.
- **What to Say:**
  > "For user comfort, we integrated a browser-persisted Dark Mode toggle.
  > 
  > If we inspect the screen on a mobile viewport (under 768px), wide tables automatically transform into touch-friendly stacked cards with 44px buttons.
  > 
  > All 30 automated pytest tests pass with 100% success. This concludes the demonstration. I am happy to take your questions."

---

## Part 2: Top 10 Likely Trainer Questions & Answers

#### Q1: Why did you choose raw PyMySQL with parameterized queries instead of an ORM like SQLAlchemy?
> **Answer:** "Using PyMySQL gives complete, transparent control over SQL query optimization and allows us to demonstrate a deep understanding of relational database design, indexing, transactions, and foreign key constraints without the abstraction of an ORM. Every query uses parameterized inputs (`%s`) to strictly prevent SQL injection."

#### Q2: How do you prevent SQL injection when the user sorts by a column in the transactions table?
> **Answer:** "SQL column names cannot be parameterized with `%s`. Therefore, we enforce an explicit whitelist in `queries.py` containing only allowed columns (`date`, `amount`, `category`, `type`). If user input doesn't match the whitelist, it defaults safely to `transaction_date`."

#### Q3: How do you ensure one user cannot see or edit another user's financial records?
> **Answer:** "Every database query includes `WHERE user_id = %s` using the `user_id` stored in Flask's secure session. When accessing `/transactions/<id>/edit` or deleting, we query the transaction by ID and verify `existing['user_id'] == current_user_id`. If there is a mismatch, we immediately return an HTTP 404 response."

#### Q4: What happens if a user records expenses in a month with zero income? Does the savings rate crash with a divide-by-zero error?
> **Answer:** "No. In `services/analytics.py`, all division operations are guarded with conditional checks. If income is zero and expenses exist, the savings rate is safely calculated as `-100.0%`. If both income and expenses are zero, it evaluates to `0.0%`. This was verified in our automated pytest test suite."

#### Q5: Why did you use Matplotlib Agg backend instead of the default backend?
> **Answer:** "Flask runs as a headless server without a graphical display window (GUI). The default Matplotlib backend tries to open a GUI window, which causes server crashes. `matplotlib.use('Agg')` uses a non-interactive raster backend that renders charts directly into in-memory byte buffers (`BytesIO`). We also call `plt.close(fig)` in a `finally` block to prevent server memory leaks."

#### Q6: How does the monthly budget batch save button work?
> **Answer:** "The form submits all category limits in one POST request. In the database query, we use MySQL's `INSERT INTO monthly_budgets (...) VALUES (...) ON DUPLICATE KEY UPDATE budget_amount = VALUES(budget_amount)`. Combined with our unique constraint on `(user_id, category_id, year, month)`, this performs an atomic upsert for all categories in a single transaction."

#### Q7: How does your application prevent double form submissions?
> **Answer:** "In `app.js`, we have a submit event listener that checks form validity. Once validated, it disables the submit button immediately, preserves the button's exact pixel width to prevent layout shift, and injects an animated Bootstrap spinner with the text 'Processing...'."

#### Q8: Where is the user's Dark Mode preference stored? In the database or browser?
> **Answer:** "It is stored entirely client-side in the browser's `localStorage` and toggles Bootstrap 5.3's `data-bs-theme` attribute on the root HTML tag. This ensures zero database overhead for purely cosmetic UI preferences while persisting across user sessions."

#### Q9: How do you handle database connection errors if MySQL stops running?
> **Answer:** "Our database utility in `db.py` wraps PyMySQL operations in `try-except` blocks. If MySQL is unreachable, it logs the technical error to the server console and raises a custom `DatabaseError` with a generic, friendly message that hides database credentials from the end user."

#### Q10: How are your automated tests structured?
> **Answer:** "We have 30 pytest tests organized into 4 modules: `test_validation.py` for input validators, `test_auth_security.py` for password hashing and verification, `test_budget_logic.py` for budget status boundaries (specifically 80% and 100%), and `test_analytics.py` for Pandas and NumPy calculations. All 30 tests pass with a 100% pass rate."
