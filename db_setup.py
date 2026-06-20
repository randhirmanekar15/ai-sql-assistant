"""Create a small demo SQLite database (sales.db) with sample data.

Kept dependency-free (stdlib sqlite3 only) so it can run and be tested without
LangChain installed.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = "sales.db"

_PRODUCTS = [
    ("Widget A", 25.0),
    ("Widget B", 40.0),
    ("Gadget C", 120.0),
]

_SALES = [
    (1, 10),
    (2, 4),
    (3, 7),
    (1, 5),
    (3, 2),
]


def build_demo_db(path: str = DB_PATH) -> str:
    """Create the demo database and return its path."""
    Path(path).unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
        )
        cur.execute(
            "CREATE TABLE sales (id INTEGER PRIMARY KEY, product_id INTEGER, units INTEGER)"
        )
        cur.executemany(
            "INSERT INTO products (name, price) VALUES (?, ?)", _PRODUCTS
        )
        cur.executemany(
            "INSERT INTO sales (product_id, units) VALUES (?, ?)", _SALES
        )
        conn.commit()
    finally:
        conn.close()
    return path


if __name__ == "__main__":
    print(f"Created {build_demo_db()}")
