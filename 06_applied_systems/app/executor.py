"""Read-only SQL executor for the Fasten_Your_Seat_Belts SQL Assistant.

Every query is executed against SQLite and restricted to read-only
`SELECT` statements. Any non-SELECT construct is rejected with a clear error.

Paths are resolved relative to this module's location so the app and the
regression suite behave identically regardless of the current working dir.
"""

import os
import sqlite3

_BAD_MARKERS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "PRAGMA",
    "ATTACH",
    "REPLACE",
)

# The demo database lives under 01_hermes_sql_agent/database/
_DB_RELATIVE = os.path.join("database", "sample_company.db")


def get_project_root():
    """Return the directory that holds 01_hermes_sql_agent/ (i.e. the repo root)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_path():
    """Absolute path to the sample SQLite database."""
    return os.path.join(get_project_root(), _DB_RELATIVE)


def get_connection(db_path=None):
    return sqlite3.connect(db_path or get_db_path())


def get_schema(conn):
    """Map table name -> CREATE statement for every table in the DB."""
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return {name: sql for name, sql in rows}


def is_read_only(query):
    upper = query.upper().strip()
    return not any(marker in upper for marker in _BAD_MARKERS)


def validate_query(conn, query):
    """Raise ValueError if the query is not a read-only SELECT."""
    if not is_read_only(query):
        raise ValueError(
            "Write / non-SELECT construct rejected. "
            "Only read-only SELECT queries are allowed."
        )
    return query.strip()


def run_query(conn, query):
    """Validate + execute a read-only query. Returns (columns, rows)."""
    validate_query(conn, query)
    cur = conn.execute(query)
    cols = [d[0] for d in cur.description] if cur.description else []
    return cols, cur.fetchall()
