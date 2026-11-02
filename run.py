"""
Home Budget Application - Entry Point
"""
import os
from app import create_app
from database.auto_init_sqlite import init_sqlite_if_needed

app = create_app()

# If running with SQLite (e.g. Render cloud), auto-initialize database tables & demo user
if app.config.get('USE_SQLITE'):
    db_file = app.config.get('SQLITE_DB_PATH', 'home_budget.db')
    init_sqlite_if_needed(db_file)

if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=True)
