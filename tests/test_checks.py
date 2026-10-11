"""Unit tests for the pure logic in scripts/checks/ (the git-calling parts run in CI)."""

from pathlib import Path

import pytest

from scripts.checks import changelog_updated, docs_allowlist, migrations_append_only

# --- migrations_append_only ------------------------------------------------------------------


def test_extract_migrations_reads_annotated_list() -> None:
    source = 'MIGRATIONS: list[str] = ["CREATE TABLE a (x)", "CREATE TABLE b (y)"]\n'

    assert migrations_append_only.extract_migrations(source) == [
        "CREATE TABLE a (x)",
        "CREATE TABLE b (y)",
    ]


def test_extract_migrations_reads_plain_assignment() -> None:
    assert migrations_append_only.extract_migrations('MIGRATIONS = ["one"]\n') == ["one"]


def test_extract_migrations_missing_returns_none() -> None:
    assert migrations_append_only.extract_migrations("OTHER = [1]\n") is None


def test_extract_migrations_rejects_non_strings() -> None:
    with pytest.raises(ValueError):
        migrations_append_only.extract_migrations("MIGRATIONS = [1, 2]\n")


def test_compare_allows_append() -> None:
    assert migrations_append_only.compare(["a"], ["a", "b"]) == []


def test_compare_flags_edit_and_removal() -> None:
    assert migrations_append_only.compare(["a", "b"], ["a", "B"]) == [
        "migration 2 was edited — append a new migration instead."
    ]
    assert migrations_append_only.compare(["a", "b"], ["a"]) == [
        "1 migration(s) removed (base has 2)."
    ]


def test_real_database_module_parses() -> None:
    source = Path(__file__).resolve().parent.parent.joinpath("app", "database.py")
    migrations = migrations_append_only.extract_migrations(source.read_text(encoding="utf-8"))

    assert migrations and "CREATE TABLE providers" in migrations[0]


# --- changelog_updated -----------------------------------------------------------------------

CHANGELOG = """# Changelog

## [Unreleased]

### Added
- New thing.

## [0.1.0] - 2026-10-10

- Old thing.
"""


def test_unreleased_entries_only_reads_unreleased_section() -> None:
    assert changelog_updated.unreleased_entries(CHANGELOG) == {"- New thing."}


def test_needs_entry_for_shipped_paths_only() -> None:
    assert changelog_updated.needs_entry(["app/main.py"])
    assert changelog_updated.needs_entry(["installer/build_run.sh"])
    assert not changelog_updated.needs_entry(["tests/test_main.py", "README.md"])


def test_skip_label_short_circuits() -> None:
    assert changelog_updated.main(["--labels", "docs,skip-changelog"]) == 0


# --- docs_allowlist --------------------------------------------------------------------------


def test_docs_allowlist_flags_unknown_files(tmp_path: Path) -> None:
    (tmp_path / "installation.md").write_text("x", encoding="utf-8")
    (tmp_path / "notes.md").write_text("x", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "plan.md").write_text("x", encoding="utf-8")

    assert docs_allowlist.disallowed(tmp_path) == ["notes.md", "sub/plan.md"]


def test_docs_allowlist_missing_dir_is_fine(tmp_path: Path) -> None:
    assert docs_allowlist.disallowed(tmp_path / "nope") == []
