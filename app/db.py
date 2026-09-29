import mysql.connector
from flask import current_app, g


def get_db():
    """Return a request-scoped MySQL connection."""
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["DB_HOST"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None, fetch_one=False):
    """Run a SELECT and return rows as dicts."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    rows = cursor.fetchone() if fetch_one else cursor.fetchall()
    cursor.close()
    return rows


def execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE. Returns the new row id (for inserts)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


def init_app(app):
    app.teardown_appcontext(close_db)
