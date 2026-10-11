from pathlib import Path

from app.database import MIGRATIONS, connect, get_db, migrate, schema_version


def test_migrate_applies_all_migrations() -> None:
    conn = connect(":memory:")

    assert schema_version(conn) == 0
    assert migrate(conn) == len(MIGRATIONS)
    assert schema_version(conn) == len(MIGRATIONS)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "providers" in tables


def test_migrate_is_idempotent() -> None:
    conn = connect(":memory:")
    migrate(conn)

    assert migrate(conn) == len(MIGRATIONS)
    versions = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
    assert versions == len(MIGRATIONS)


def test_connect_creates_parent_directory(tmp_path: Path) -> None:
    db_file = tmp_path / "nested" / "dir" / "app.db"

    connect(str(db_file)).close()

    assert db_file.exists()


def test_get_db_yields_migrated_connection_and_closes_it() -> None:
    dependency = get_db()
    conn = next(dependency)
    assert schema_version(conn) == len(MIGRATIONS)

    dependency.close()

    try:
        conn.execute("SELECT 1")
    except Exception as exc:  # sqlite3.ProgrammingError: closed database
        assert "closed" in str(exc)
    else:
        raise AssertionError("connection should be closed")
