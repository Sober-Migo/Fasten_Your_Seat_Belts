"""One-time generator for the sample SQLite demo database.

Creates 01_hermes_sql_agent/database/sample_company.db with two tables
(customers, orders) and a handful of rows used to exercise the SQL
Analyzer skill and its read-only regression tests.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sample_company.db")


def build_db(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            amount REAL,
            order_date TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        );
    """)

    cursor.executemany(
        "INSERT OR IGNORE INTO customers VALUES (?, ?, ?)",
        [
            (1, "Ahmed Magdy", "Egypt"),
            (2, "John Doe", "USA"),
            (3, "Sarah Connor", "UK"),
        ],
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)",
        [
            (101, 1, 1500.0, "2026-10-01"),
            (102, 1, 2300.0, "2026-10-15"),
            (103, 2, 450.0, "2026-10-20"),
            (104, 3, 3100.0, "2026-11-01"),
        ],
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    build_db(DB_PATH)
    print(f"Sample database created successfully at: {DB_PATH}")
