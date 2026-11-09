"""Database helpers: connection for the FastAPI service."""

import sqlite3

from .executor import get_db_path


def get_connection(db_path=None):
    """Open a connection to the sample SQLite database."""
    return sqlite3.connect(db_path or get_db_path())
