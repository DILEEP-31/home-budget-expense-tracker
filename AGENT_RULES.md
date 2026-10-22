# Agent Rules

**Section 1: Project Overview**
- Project name: Home Budget (Expense Tracker and Analysis System)
- Full‑stack Flask website, intermediate difficulty.
- Uses MySQL (real), Pandas, NumPy, Matplotlib, Chart.js, Bootstrap 5, etc.

**Section 2: Two Submissions**
- Week 1: Working first version with core features, MySQL integration, responsive UI.
- Week 2: Extend same codebase with auth, budgets, reports, tests, polish.

**Section 3: Fixed Technology Stack**
- Python 3.11/3.12, Flask 3.x, Jinja2, blueprints, app factory.
- MySQL 8 via PyMySQL (+cryptography for auth).
- Bootstrap 5, Bootstrap Icons, custom CSS/JS.
- Pandas, NumPy, Matplotlib (Agg), Chart.js.
- python‑dotenv, Werkzeug, Flask‑WTF, pytest.

**Section 4: Folder Structure**
```
home-budget-tracker/
  app/
    __init__.py
    config.py
    db.py
    utils.py
    auth/          # Week 2
    routes/
      main.py
      transactions.py
      categories.py
      # Week 2: budgets.py, reports.py, api.py
    services/
      queries.py
      # Week 2: analytics.py, budget_logic.py, charts.py
    templates/
      base.html
      home.html
      dashboard.html
      errors/
      transactions/
      categories/
      partials/
      # Week 2: auth/, budgets/, reports/
    static/
      css/style.css
      js/app.js
      # Week 2: js/charts.js
      img/
  database/
    schema.sql
    init_db.py
    seed_sample_data.py
    # Week 2: create_demo_user.py, migrations/
  docs/           # Week 2 documentation
  tests/
  .vscode/
  .env.example
  .gitignore
  requirements.txt
  run.py
  README.md
  PROGRESS.md
  AGENT_RULES.md
```

**Section 5: Database Design**
- Database `home_budget_db` (InnoDB, utf8mb4).
- Tables: `users`, `categories`, `transactions`, `monthly_budgets` with described columns, constraints, indexes, and enum types.
- Default categories with distinct colors and icons.

**Section 6: UI/UX Requirements**
- Modern fintech look, deep indigo primary, teal accent, green for income, rose/red for expense, amber warnings.
- CSS variables, Inter/Poppins font, rounded cards, shadows, responsive sidebar/off‑canvas, summary cards, charts, toast messages, disabled placeholders for Week 2 features.

**Section 7: Code Quality & Security**
- Separate files, clear comments, parameterized SQL only, whitelist for ORDER BY.
- Server‑side validation, Jinja auto‑escaping, commit/rollback, no secrets in code, friendly error messages, logging technical details.

**Section 8: Working Rules**
1. Inspect workspace first.
2. Plan before coding.
3. Small, verifiable steps.
4. Complete Week 1 before Week 2.
5. No placeholder fake data.
6. Run & test each feature.
7. Explain file changes.
8. Verify results – label VERIFIED/NOT VERIFIED/FAILED.
9. Preserve existing working code.
10. Ask before destructive actions.
11. PowerShell commands only.
12. Do not assume MySQL is running; report errors.
13. No extra libraries without ask.
14. Ask one short clarifying question if needed.
15. Keep code beginner‑readable.

**Section 9: Progress Tracking**
- Use `PROGRESS.md` with sections: Current Phase, Completed Tasks, Pending Tasks, Known Issues, Next Steps, Last Verified Commands.
- Store these rules in `AGENT_RULES.md`.

**Section 10: Standard Report Format**
1. What I did
2. Files created
3. Files modified
4. Commands run & results
5. Verification table
6. Known issues
7. Completed / Pending / Next steps
8. Manual tasks for the student

**Section 11: First Task**
- Inspect workspace, check Python/pip/MySQL, create rule & progress files, summarize project, stop before code.
