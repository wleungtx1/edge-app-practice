"""SQLite access and schema migrations.

MIGRATIONS is append-only: once a migration is on master it may never be edited, reordered or
removed — add a new one at the end instead. scripts/checks/migrations_append_only.py enforces this
in CI by comparing this list with the one on origin/master.
"""

import sqlite3
from collections.abc import Generator
from pathlib import Path

from app.config import get_settings

MIGRATIONS: list[str] = [
    # 1 — providers table
    """
    CREATE TABLE providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 1
    )
    """,
]


def connect(db_path: str) -> sqlite3.Connection:
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def schema_version(conn: sqlite3.Connection) -> int:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
    row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
    return int(row[0] or 0)


def migrate(conn: sqlite3.Connection) -> int:
    """Apply every migration not yet applied; return the resulting schema version."""
    current = schema_version(conn)
    for number, sql in enumerate(MIGRATIONS[current:], start=current + 1):
        with conn:
            conn.execute(sql)
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (number,))
    return len(MIGRATIONS)


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency: a migrated connection for the duration of one request."""
    conn = connect(get_settings().db_path)
    try:
        migrate(conn)
        yield conn
    finally:
        conn.close()
