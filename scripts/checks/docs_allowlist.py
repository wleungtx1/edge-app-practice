"""Fail if docs/ contains anything other than the allowed user-facing documents.

Usage: python scripts/checks/docs_allowlist.py

docs/ ships with the product; planning notes, history and scratch files belong in local-doc/
(git-ignored) instead.
"""

import sys
from pathlib import Path

DOCS_DIR = Path("docs")
ALLOWED = frozenset(
    {
        "installation.md",
        "architecture.md",
        "configuration.md",
        "operations.md",
        "troubleshooting.md",
        "upgrade.md",
    }
)


def disallowed(docs_dir: Path) -> list[str]:
    """Return paths (relative to docs_dir, POSIX style) that are not on the allowlist."""
    if not docs_dir.is_dir():
        return []
    return sorted(
        path.relative_to(docs_dir).as_posix()
        for path in docs_dir.rglob("*")
        if path.is_file() and path.relative_to(docs_dir).as_posix() not in ALLOWED
    )


def main() -> int:
    bad = disallowed(DOCS_DIR)
    for name in bad:
        print(f"docs: {DOCS_DIR.as_posix()}/{name} is not on the allowlist.", file=sys.stderr)
    if bad:
        print(f"docs: allowed files are {', '.join(sorted(ALLOWED))}.", file=sys.stderr)
        return 1
    print("docs: OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
