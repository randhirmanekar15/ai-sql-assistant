"""Tests for the demo DB builder (no LangChain / model required)."""

import sqlite3

from db_setup import build_demo_db


def test_build_demo_db_creates_tables(tmp_path):
    db = build_demo_db(str(tmp_path / "sales.db"))
    conn = sqlite3.connect(db)
    try:
        names = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        assert {"products", "sales"} <= names
        products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        assert products == 3
    finally:
        conn.close()
