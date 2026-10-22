"""
Seed realistic sample transactions for Home Budget Tracker.
Generates 3 months of realistic financial transactions for Demo User (user_id = 1).
Dates are calculated dynamically relative to today's date so the current month,
previous month, and two months prior all have realistic data.

Skips seeding if transactions already exist, unless run with '--force'.
'--force' prompts for manual user confirmation before removing and re-seeding.
"""
import os
import sys
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv
import pymysql

# Load environment
load_dotenv()

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'home_budget_db')
DB_USER = os.environ.get('DB_USER', 'budget_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')


def get_db_connection():
    """Returns connection to home_budget_db."""
    try:
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as err:
        print(f"\n[ERROR] Unable to connect to MySQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}.")
        print(f"Details: {err}\n")
        sys.exit(1)


def seed_data(force=False):
    """Inserts ~3 months of transactions for demo user (user_id = 1)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verify demo user exists
            cursor.execute("SELECT user_id FROM users WHERE user_id = 1;")
            user = cursor.fetchone()
            if not user:
                print("[ERROR] Demo user (user_id = 1) does not exist! Please run init_db.py first.")
                sys.exit(1)

            # Check if transactions already exist
            cursor.execute("SELECT COUNT(*) AS total FROM transactions WHERE user_id = 1;")
            existing_count = cursor.fetchone()['total']

            if existing_count > 0 and not force:
                print(f"[INFO] Sample transactions already exist ({existing_count} records found). Skipping seeding.")
                print("Tip: Run with 'python database/seed_sample_data.py --force' if you wish to re-seed.")
                return

            if existing_count > 0 and force:
                print(f"\n[WARNING] Found {existing_count} existing transactions.")
                confirm = input("Type 'YES' to delete existing transactions and re-seed: ").strip()
                if confirm == 'YES':
                    cursor.execute("DELETE FROM transactions WHERE user_id = 1;")
                    conn.commit()
                    print("[OK] Existing transactions cleared.")
                else:
                    print("Re-seeding cancelled.")
                    return

            # Fetch category IDs mapping: category_name -> category_id
            cursor.execute("SELECT category_id, category_name, category_type FROM categories;")
            categories = {row['category_name']: row['category_id'] for row in cursor.fetchall()}

            # Generate dynamic transaction dates based on today's date
            today = date.today()

            # Realistic transaction template
            # (category_name, type, amount, day_offset_from_today, description)
            sample_records = [
                # Current Month Transactions
                ('Salary', 'income', 65000.00, today.day - 1, 'Monthly Salary Deposit'),
                ('Rent', 'expense', 18000.00, today.day - 2, 'Apartment Monthly Rent'),
                ('Groceries', 'expense', 3450.50, 1, 'Supermarket Weekly Groceries'),
                ('Utilities', 'expense', 2200.00, 3, 'Electricity and Water Bill'),
                ('Dining Out', 'expense', 1450.00, 2, 'Weekend Dinner with Friends'),
                ('Transportation', 'expense', 1800.00, 4, 'Metro Card Recharge & Fuel'),
                ('Freelance', 'income', 12500.00, 5, 'Web Design Project Payment'),
                ('Shopping', 'expense', 2899.00, 6, 'Clothing and Essentials'),
                ('Entertainment', 'expense', 699.00, 7, 'Streaming Subscriptions'),
                ('Groceries', 'expense', 2150.00, 8, 'Fresh Fruits and Vegetables'),

                # Month - 1 (Approx 30 days ago)
                ('Salary', 'income', 65000.00, 31, 'Monthly Salary Deposit'),
                ('Rent', 'expense', 18000.00, 32, 'Apartment Monthly Rent'),
                ('Groceries', 'expense', 4120.00, 35, 'Monthly Bulk Pantry Shopping'),
                ('Utilities', 'expense', 2450.00, 38, 'Electricity & Broadband Bill'),
                ('Healthcare', 'expense', 1850.00, 40, 'Routine Health Checkup & Medicine'),
                ('Dining Out', 'expense', 2100.00, 42, 'Family Birthday Dinner'),
                ('Gifts', 'income', 5000.00, 44, 'Festival Cash Gift'),
                ('Transportation', 'expense', 2200.00, 46, 'Cab rides & Fuel'),
                ('Entertainment', 'expense', 1200.00, 50, 'Movie Tickets & Snacks'),
                ('Shopping', 'expense', 3500.00, 55, 'Home Improvement Tools'),

                # Month - 2 (Approx 60-75 days ago)
                ('Salary', 'income', 65000.00, 62, 'Monthly Salary Deposit'),
                ('Rent', 'expense', 18000.00, 63, 'Apartment Monthly Rent'),
                ('Groceries', 'expense', 3800.00, 65, 'Supermarket Grocery Run'),
                ('Investments', 'income', 8500.00, 67, 'Stock Dividend Payout'),
                ('Utilities', 'expense', 1950.00, 70, 'Water & Gas Connection Bill'),
                ('Education', 'expense', 4500.00, 72, 'Online Certification Course'),
                ('Dining Out', 'expense', 1850.00, 75, 'Dinner with Colleagues'),
                ('Transportation', 'expense', 1600.00, 78, 'Train Passes and Local Transit'),
                ('Other Expense', 'expense', 850.00, 80, 'Key Replacement and Hardware'),
                ('Freelance', 'income', 15000.00, 85, 'Consulting Work Milestone 1')
            ]

            insert_query = """
                INSERT INTO transactions 
                    (user_id, category_id, transaction_type, amount, transaction_date, description)
                VALUES 
                    (%s, %s, %s, %s, %s, %s);
            """

            inserted = 0
            for cat_name, t_type, amount, days_ago, desc in sample_records:
                cat_id = categories.get(cat_name)
                if not cat_id:
                    print(f"[SKIP] Unknown category '{cat_name}'.")
                    continue
                # Calculate valid date
                tx_date = today - timedelta(days=days_ago)
                cursor.execute(insert_query, (1, cat_id, t_type, amount, tx_date, desc))
                inserted += 1

            conn.commit()
            print(f"[OK] Successfully seeded {inserted} realistic transactions across 3 months.")

    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seed realistic sample transactions.")
    parser.add_argument('--force', action='store_true', help="Force re-seeding even if transactions already exist.")
    args = parser.parse_args()

    print("Seeding sample data for Home Budget Tracker...")
    seed_data(force=args.force)
    print("Sample data seeding finished!\n")
