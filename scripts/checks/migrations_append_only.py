"""Fail if app/database.py MIGRATIONS is not an append-only extension of the base branch's.

Usage: python scripts/checks/migrations_append_only.py [--base origin/master]

Migrations already on the base branch may not be edited, reordered or removed; new ones may only
be appended. Both lists are read with `ast` (never imported), the base one via `git show`.
"""

import argparse
import ast
import subprocess
import sys
from pathlib import Path

DATABASE_FILE = "app/database.py"
VARIABLE = "MIGRATIONS"


def extract_migrations(source: str) -> list[str] | None:
    """Return the literal MIGRATIONS list in `source`, or None if it is not defined."""
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        if any(isinstance(t, ast.Name) and t.id == VARIABLE for t in targets):
            value = ast.literal_eval(node.value)  # type: ignore[arg-type]
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise ValueError(f"{VARIABLE} must be a literal list of strings")
            return value
    return None


def compare(base: list[str], head: list[str]) -> list[str]:
    """Return error messages; empty when `head` only appends to `base`."""
    errors: list[str] = []
    if len(head) < len(base):
        errors.append(f"{len(base) - len(head)} migration(s) removed (base has {len(base)}).")
    for number, (old, new) in enumerate(zip(base, head, strict=False), start=1):
        if old != new:
            errors.append(f"migration {number} was edited — append a new migration instead.")
    return errors


def git_show(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout if result.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/master", help="git ref to compare against")
    args = parser.parse_args(argv)

    base_source = git_show(args.base, DATABASE_FILE)
    if base_source is None:
        print(f"migrations: {DATABASE_FILE} not found at {args.base} — nothing to compare.")
        return 0
    base = extract_migrations(base_source) or []
    head = extract_migrations(Path(DATABASE_FILE).read_text(encoding="utf-8")) or []

    errors = compare(base, head)
    for error in errors:
        print(f"migrations: {error}", file=sys.stderr)
    if not errors:
        print(f"migrations: OK ({len(base)} on {args.base}, {len(head) - len(base)} new).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
