"""
Database connection and query execution helper supporting both MySQL and SQLite.
In local development with MySQL running, connects seamlessly via PyMySQL.
In cloud/Render environments without MySQL, transparently falls back to SQLite.
"""
import os
import re
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from flask import current_app


class DatabaseError(Exception):
    """Custom exception class for friendly database error reporting."""
    pass


def _adapt_query_for_sqlite(query):
    """
    Translates MySQL-specific SQL syntax into SQLite-compatible SQL syntax.
    1. Replaces %s placeholders with ?
    2. Replaces YEAR(col) with cast(strftime('%Y', col) as integer)
    3. Replaces MONTH(col) with cast(strftime('%m', col) as integer)
    4. Handles INSERT INTO ... ON DUPLICATE KEY UPDATE
    """
    q = query

    # Convert YEAR(col) -> CAST(strftime('%Y', col) AS INTEGER)
    q = re.sub(r'YEAR\(([^)]+)\)', r"CAST(strftime('%Y', \1) AS INTEGER)", q, flags=re.IGNORECASE)

    # Convert MONTH(col) -> CAST(strftime('%m', col) AS INTEGER)
    q = re.sub(r'MONTH\(([^)]+)\)', r"CAST(strftime('%m', \1) AS INTEGER)", q, flags=re.IGNORECASE)

    # Convert INSERT ... ON DUPLICATE KEY UPDATE -> INSERT OR REPLACE INTO ...
    if "ON DUPLICATE KEY UPDATE" in q.upper():
        # Match "INSERT INTO tablename (cols) VALUES (vals) ON DUPLICATE KEY UPDATE ..."
        match = re.search(r"INSERT\s+INTO\s+([a-zA-Z0-9_]+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)", q, flags=re.IGNORECASE)
        if match:
            table = match.group(1)
            cols = match.group(2)
            vals = match.group(3)
            q = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({vals})"

    # Convert %s placeholders to ?
    q = q.replace('%s', '?')
    return q


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db_connection():
    """
    Creates and returns a connection to either MySQL or SQLite.
    """
    use_sqlite = current_app.config.get('USE_SQLITE', False)

    if use_sqlite:
        db_path = current_app.config.get('SQLITE_DB_PATH', 'home_budget.db')
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = _dict_factory
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            print(f"[SQLITE CONNECTION ERROR] {e}")
            raise DatabaseError("Unable to establish SQLite database connection.")

    try:
        connection = pymysql.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=False
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"[DB CONNECTION ERROR] Code: {e.args[0] if e.args else 'Unknown'}, Message: {str(e)}")
        raise DatabaseError("Unable to establish a secure connection to the database. Please verify the database service is running.")


def query_db(query, params=None, one=False):
    """
    Safely executes a SELECT query with parameterized inputs across MySQL or SQLite.
    """
    use_sqlite = current_app.config.get('USE_SQLITE', False)
    connection = get_db_connection()

    if use_sqlite:
        try:
            sql = _adapt_query_for_sqlite(query)
            cursor = connection.cursor()
            cursor.execute(sql, tuple(params) if params else ())
            result = cursor.fetchall()
            return (result[0] if result else None) if one else result
        except sqlite3.Error as e:
            print(f"[SQLITE QUERY ERROR] Query: {query} | Error: {e}")
            raise DatabaseError("A database query error occurred while retrieving data.")
        finally:
            connection.close()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return (result[0] if result else None) if one else result
    except pymysql.MySQLError as e:
        print(f"[DB QUERY ERROR] Query: {query} | Error: {e}")
        raise DatabaseError("A database query error occurred while retrieving data.")
    finally:
        connection.close()


def execute_db(query, params=None):
    """
    Safely executes an INSERT, UPDATE, or DELETE query.
    """
    use_sqlite = current_app.config.get('USE_SQLITE', False)
    connection = get_db_connection()

    if use_sqlite:
        try:
            sql = _adapt_query_for_sqlite(query)
            cursor = connection.cursor()
            cursor.execute(sql, tuple(params) if params else ())
            connection.commit()
            last_id = cursor.lastrowid
            affected_rows = cursor.rowcount
            return last_id if last_id else affected_rows
        except sqlite3.Error as e:
            connection.rollback()
            print(f"[SQLITE EXECUTE ERROR] Query: {query} | Error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            connection.close()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            affected_rows = cursor.rowcount
        connection.commit()
        return last_id if last_id else affected_rows
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"[DB EXECUTE ERROR] Query: {query} | Error: {e}")
        raise DatabaseError(f"Database operation failed: {e.args[1] if len(e.args) > 1 else 'Constraint or syntax error'}")
    finally:
        connection.close()
