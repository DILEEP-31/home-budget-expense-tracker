"""
Database Initialization Script for Home Budget Tracker.
Reads configuration from .env, creates the database if not present,
creates all required tables using CREATE TABLE IF NOT EXISTS,
inserts default categories (without duplicates), and adds a demo user.

Supports optional '--reset' argument which prompts for confirmation before dropping tables.
Safe to run repeatedly.
"""
import os
import sys
import argparse
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv()

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'home_budget_db')
DB_USER = os.environ.get('DB_USER', 'budget_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

# Default Categories per Section 5 of specification
DEFAULT_CATEGORIES = [
    # Expense Categories (10)
    ('Groceries', 'expense', '#10B981', 'bi-cart-check'),
    ('Rent', 'expense', '#EF4444', 'bi-house-door'),
    ('Transportation', 'expense', '#F59E0B', 'bi-fuel-pump'),
    ('Healthcare', 'expense', '#EC4899', 'bi-heart-pulse'),
    ('Education', 'expense', '#8B5CF6', 'bi-mortarboard'),
    ('Entertainment', 'expense', '#6366F1', 'bi-controller'),
    ('Utilities', 'expense', '#3B82F6', 'bi-lightning-charge'),
    ('Shopping', 'expense', '#F97316', 'bi-bag'),
    ('Dining Out', 'expense', '#14B8A6', 'bi-cup-hot'),
    ('Other Expense', 'expense', '#6B7280', 'bi-three-dots'),
    # Income Categories (5)
    ('Salary', 'income', '#059669', 'bi-cash-stack'),
    ('Freelance', 'income', '#0D9488', 'bi-laptop'),
    ('Gifts', 'income', '#D97706', 'bi-gift'),
    ('Investments', 'income', '#4F46E5', 'bi-graph-up-arrow'),
    ('Other Income', 'income', '#4B5563', 'bi-wallet2')
]


def get_server_connection():
    """Connect to MySQL server without selecting a database."""
    try:
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as err:
        print(f"\n[ERROR] Could not connect to MySQL server at {DB_HOST}:{DB_PORT}.")
        print(f"Details: {err}")
        print("\nPlease check:")
        print("  1. Is MySQL Server running? (e.g. Start-Service MySQL267)")
        print("  2. Are DB_USER and DB_PASSWORD correct in your .env file?")
        print(f"  3. Does user '{DB_USER}' have access permissions?\n")
        sys.exit(1)


def init_database(reset=False):
    """Initializes the database schema, categories, and demo user."""
    conn = get_server_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Create database if it does not exist
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            cursor.execute(f"USE `{DB_NAME}`;")

            # 2. Handle --reset flag
            if reset:
                print("\n[WARNING] You requested a database reset!")
                confirm = input("Type 'YES' to confirm dropping all tables: ").strip()
                if confirm == 'YES':
                    print("Dropping existing tables...")
                    cursor.execute("DROP TABLE IF EXISTS monthly_budgets;")
                    cursor.execute("DROP TABLE IF EXISTS transactions;")
                    cursor.execute("DROP TABLE IF EXISTS categories;")
                    cursor.execute("DROP TABLE IF EXISTS users;")
                    conn.commit()
                    print("Existing tables dropped successfully.")
                else:
                    print("Reset cancelled. Proceeding with existing schema.")

            # 3. Read and execute schema.sql
            schema_file_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if not os.path.exists(schema_file_path):
                print(f"[ERROR] schema.sql not found at {schema_file_path}")
                sys.exit(1)

            with open(schema_file_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # Execute DDL statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                except pymysql.MySQLError as e:
                    # Ignore duplicate index errors if running repeatedly
                    if e.args[0] == 1061:  # Duplicate key name
                        pass
                    else:
                        raise e
            conn.commit()
            print("[OK] All database tables verified / created.")

            # 4. Insert Demo User if not exists
            # Single demo user for Week 1 (user_id = 1)
            cursor.execute("SELECT user_id FROM users WHERE user_id = 1;")
            demo_user = cursor.fetchone()
            if not demo_user:
                cursor.execute(
                    """
                    INSERT INTO users (user_id, full_name, email, password_hash)
                    VALUES (1, %s, %s, %s);
                    """,
                    (
                        "Demo User",
                        "demo@example.com",
                        "WEEK1_DEMO_PLACEHOLDER_HASH"  # Real authentication arrives in Week 2
                    )
                )
                conn.commit()
                print("[OK] Demo user created (user_id: 1, email: demo@example.com).")
            else:
                print("[INFO] Demo user (user_id: 1) already exists.")

            # 5. Insert Default Categories without duplicates
            inserted_count = 0
            for name, cat_type, color, icon in DEFAULT_CATEGORIES:
                cursor.execute(
                    """
                    INSERT INTO categories (category_name, category_type, color, icon)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        color = VALUES(color),
                        icon = VALUES(icon);
                    """,
                    (name, cat_type, color, icon)
                )
                if cursor.rowcount == 1:
                    inserted_count += 1
            conn.commit()
            print(f"[OK] Default categories verified ({len(DEFAULT_CATEGORIES)} total categories ready).")

    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initialize Home Budget MySQL Database.")
    parser.add_argument('--reset', action='store_true', help="Drop existing tables and recreate them (requires confirmation).")
    args = parser.parse_args()

    print(f"Connecting to MySQL ({DB_HOST}:{DB_PORT}) as '{DB_USER}'...")
    init_database(reset=args.reset)
    print("Database initialization complete!\n")
