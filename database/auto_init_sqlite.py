"""
Auto-initialization helper for cloud deployment (e.g. Render).
Ensures tables exist, categories are seeded, and the demo user is populated
when running in SQLite fallback mode.
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash


def init_sqlite_if_needed(db_path):
    """Creates tables and populates default demo data if SQLite database is empty."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            category_type TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT '#4F46E5',
            icon TEXT NOT NULL DEFAULT 'bi-tag',
            UNIQUE(category_name, category_type)
        );
    """)

    # 3. Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            transaction_date TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );
    """)

    # 4. Monthly Budgets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_budgets (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            budget_year INTEGER NOT NULL,
            budget_month INTEGER NOT NULL,
            budget_amount REAL NOT NULL CHECK(budget_amount >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id),
            UNIQUE(user_id, category_id, budget_year, budget_month)
        );
    """)
    conn.commit()

    # Seed Categories if empty
    cursor.execute("SELECT count(*) FROM categories;")
    if cursor.fetchone()[0] == 0:
        categories = [
            # Expense Categories
            ('Groceries', 'expense', '#10B981', 'bi-cart3'),
            ('Rent', 'expense', '#EF4444', 'bi-house-door'),
            ('Utilities', 'expense', '#F59E0B', 'bi-lightning-charge'),
            ('Entertainment', 'expense', '#8B5CF6', 'bi-film'),
            ('Transportation', 'expense', '#06B6D4', 'bi-fuel-pump'),
            ('Healthcare', 'expense', '#EC4899', 'bi-heart-pulse'),
            ('Dining Out', 'expense', '#F97316', 'bi-cup-hot'),
            ('Education', 'expense', '#3B82F6', 'bi-book'),
            ('Shopping', 'expense', '#6366F1', 'bi-bag'),
            ('Miscellaneous', 'expense', '#64748B', 'bi-three-dots'),
            # Income Categories
            ('Salary', 'income', '#059669', 'bi-briefcase'),
            ('Freelance', 'income', '#0D9488', 'bi-laptop'),
            ('Investments', 'income', '#14B8A6', 'bi-graph-up-arrow'),
            ('Gift / Bonus', 'income', '#10B981', 'bi-gift'),
            ('Other Income', 'income', '#64748B', 'bi-cash-coin')
        ]
        cursor.executemany("INSERT INTO categories (category_name, category_type, color, icon) VALUES (?, ?, ?, ?);", categories)
        conn.commit()

    # Seed Demo User if not exists
    cursor.execute("SELECT user_id FROM users WHERE email = 'demo@example.com';")
    row = cursor.fetchone()
    if not row:
        demo_hash = generate_password_hash("Demo@1234")
        cursor.execute("INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?);", ("Demo User", "demo@example.com", demo_hash))
        conn.commit()
        demo_user_id = cursor.lastrowid
    else:
        demo_user_id = row[0]

    # Seed sample transactions if none exist
    cursor.execute("SELECT count(*) FROM transactions WHERE user_id = ?;", (demo_user_id,))
    if cursor.fetchone()[0] == 0:
        txs = [
            (demo_user_id, 11, 'income', 65000.0, '2026-10-01', 'Monthly Salary Credit'),
            (demo_user_id, 1, 'expense', 4500.0, '2026-10-05', 'Weekly Groceries Mart'),
            (demo_user_id, 2, 'expense', 18000.0, '2026-10-02', 'House Rent Payment'),
            (demo_user_id, 3, 'expense', 2400.0, '2026-10-10', 'Electricity & Water Bill'),
            (demo_user_id, 4, 'expense', 1200.0, '2026-10-12', 'Movie & Weekend Fun'),
            (demo_user_id, 5, 'expense', 3500.0, '2026-10-08', 'Monthly Metro Pass & Fuel'),
            (demo_user_id, 12, 'income', 12000.0, '2026-10-15', 'Freelance Web Design'),
            (demo_user_id, 7, 'expense', 1800.0, '2026-10-18', 'Weekend Dining with Family'),
            (demo_user_id, 9, 'expense', 2098.75, '2026-10-20', 'Festival Shopping')
        ]
        cursor.executemany("""
            INSERT INTO transactions (user_id, category_id, transaction_type, amount, transaction_date, description)
            VALUES (?, ?, ?, ?, ?, ?);
        """, txs)

        # Sample Budgets
        budgets = [
            (demo_user_id, 1, 2026, 10, 5000.0),
            (demo_user_id, 2, 2026, 10, 18000.0),
            (demo_user_id, 3, 2026, 10, 3000.0),
            (demo_user_id, 4, 2026, 10, 2000.0),
            (demo_user_id, 5, 2026, 10, 4000.0)
        ]
        cursor.executemany("""
            INSERT OR REPLACE INTO monthly_budgets (user_id, category_id, budget_year, budget_month, budget_amount)
            VALUES (?, ?, ?, ?, ?);
        """, budgets)
        conn.commit()

    conn.close()
