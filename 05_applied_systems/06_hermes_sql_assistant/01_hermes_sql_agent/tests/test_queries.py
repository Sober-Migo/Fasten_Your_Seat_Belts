# SQL Database Analyzer — Regression Tests

# Read-only queries that validate schema and results for the
# `sample_company.db` SQLite demo database. These tests exercise only
# `SELECT` statements.

import os
import sqlite3
import sys

# Resolve paths relative to the project root so the suite runs from any
# working directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
DB_PATH = os.path.join(_PROJECT_ROOT, "database", "sample_company.db")

# Hard expections: an INSERT/UPDATE/DELETE/DROP anywhere in a candidate query fails validation.
BAD_MARKERS = ("INSERT", "UPDATE", "DELETE", "DROP", "PRAGMA", "ATTACH", "REPLACE")


def get_schema(conn):
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return {name: sql for name, sql in rows}


def is_read_only(query):
    upper = query.upper().strip()
    return not any(marker in upper for marker in BAD_MARKERS)


def validate_query(conn, query):
    """Raise on any non-read-only construct. Returns normalized query."""
    assert is_read_only(query), f"Write/non-SELECT construct rejected: {query!r}"
    return query.strip()


def run_query(conn, query):
    validate_query(conn, query)
    cur = conn.execute(query)
    cols = [d[0] for d in cur.description] if cur.description else []
    return cols, cur.fetchall()


def test_tables_exist():
    conn = sqlite3.connect(DB_PATH)
    try:
        schema = get_schema(conn)
        assert {"customers", "orders"} <= set(schema.keys()), schema.keys()
    finally:
        conn.close()


def test_customers_rows():
    conn = sqlite3.connect(DB_PATH)
    try:
        _, rows = run_query(conn, "SELECT * FROM customers")
        names = [r[1] for r in rows]
        assert "Ahmed Magdy" in names
        assert "John Doe" in names
        assert "Sarah Connor" in names
    finally:
        conn.close()


def test_orders_amount_sum():
    conn = sqlite3.connect(DB_PATH)
    try:
        _, rows = run_query(conn, """
            SELECT SUM(o.amount) AS total, COUNT(*) AS n
            FROM orders o
        """)
        total, n = rows[0]
        assert n == 4
        assert total == 7350.0
    finally:
        conn.close()


def test_customers_orders_join():
    conn = sqlite3.connect(DB_PATH)
    try:
        _, rows = run_query(conn, """
            SELECT c.name, o.amount
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            ORDER BY o.amount DESC
        """)
        assert rows[0][0] == "Sarah Connor"  # 3100.0 largest
        assert rows[1][0] == "Ahmed Magdy"  # 2300.0
    finally:
        conn.close()


if __name__ == "__main__":
    import traceback
    conn = sqlite3.connect(DB_PATH)
    failed = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:
                failed.append(name)
                print(f"FAIL {name}")
                traceback.print_exc()
    conn.close()
    print(f"\n{len(failed)}/{sum(1 for k,v in globals().items() if k.startswith('test_') and callable(v))} tests failed")
    sys.exit(1 if failed else 0)

