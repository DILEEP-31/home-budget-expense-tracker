"""
Database connection and safe parameterized query execution helpers.
Uses PyMySQL with DictCursor.
Ensures automatic commits on write, rollbacks on error, and guaranteed connection closure.
Hides credentials and sensitive connection strings from end-user error messages.
"""
import pymysql
from pymysql.cursors import DictCursor
from flask import current_app


class DatabaseError(Exception):
    """Custom exception class for friendly database error reporting."""
    pass


def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.
    Configuration is read from Flask current_app.config.
    """
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
        # Log technical error safely on terminal
        print(f"[DB CONNECTION ERROR] Code: {e.args[0] if e.args else 'Unknown'}, Message: {str(e)}")
        # Raise generic message that hides database credentials
        raise DatabaseError("Unable to establish a secure connection to the database. Please verify the database service is running.")


def query_db(query, params=None, one=False):
    """
    Safely executes a SELECT query with parameterized inputs.
    
    :param query: SQL query string with %s placeholders
    :param params: Tuple or list of query parameters
    :param one: If True, returns a single dictionary row (or None)
    :return: List of dict rows, or single dict row, or None
    """
    connection = get_db_connection()
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
    Safely executes an INSERT, UPDATE, or DELETE query with parameterized inputs.
    Commits on success, rolls back on exception, and always closes the connection.
    
    :param query: SQL statement with %s placeholders
    :param params: Tuple or list of statement parameters
    :return: The last inserted row ID (if applicable) or affected rows count
    """
    connection = get_db_connection()
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
