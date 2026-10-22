"""
Script to create or update the demo user with a valid hashed password.
Sets email: demo@example.com, password: Demo@1234
Ensures user_id = 1 is preserved so Week 1 seed transactions remain visible.
"""
import os
import sys
from dotenv import load_dotenv
import pymysql
from werkzeug.security import generate_password_hash

load_dotenv()

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'home_budget_db')
DB_USER = os.environ.get('DB_USER', 'budget_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

DEMO_EMAIL = "demo@example.com"
DEMO_NAME = "Demo User"
DEMO_PASSWORD = "Demo@1234"


def setup_demo_user():
    """Configures demo account in MySQL."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as err:
        print(f"[ERROR] Cannot connect to database: {err}")
        sys.exit(1)

    try:
        with conn.cursor() as cursor:
            hashed_pw = generate_password_hash(DEMO_PASSWORD, method='scrypt')

            # Check if user_id 1 or demo email already exists
            cursor.execute("SELECT user_id, email FROM users WHERE user_id = 1 OR email = %s;", (DEMO_EMAIL,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE users 
                    SET full_name = %s, email = %s, password_hash = %s 
                    WHERE user_id = %s;
                    """,
                    (DEMO_NAME, DEMO_EMAIL, hashed_pw, existing['user_id'])
                )
                conn.commit()
                print(f"[OK] Demo user (ID: {existing['user_id']}, Email: {DEMO_EMAIL}) updated with secure Werkzeug hash.")
            else:
                cursor.execute(
                    """
                    INSERT INTO users (user_id, full_name, email, password_hash)
                    VALUES (1, %s, %s, %s);
                    """,
                    (DEMO_NAME, DEMO_EMAIL, hashed_pw)
                )
                conn.commit()
                print(f"[OK] Demo user (ID: 1, Email: {DEMO_EMAIL}) created with secure Werkzeug hash.")

            print(f"Credentials for testing:")
            print(f"  Email:    {DEMO_EMAIL}")
            print(f"  Password: {DEMO_PASSWORD}")
    finally:
        conn.close()


if __name__ == '__main__':
    print("Setting up demo user with secure password hash...")
    setup_demo_user()
