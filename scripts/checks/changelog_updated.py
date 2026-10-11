"""Fail if a change to shipped files has no new line under CHANGELOG.md's [Unreleased] heading.

Usage: python scripts/checks/changelog_updated.py [--base origin/master] [--labels a,b]

Shipped files are those under app/, templates/, static/ and installer/. A pull request labelled
`skip-changelog` passes regardless (CI passes the PR's labels via --labels).
"""

import argparse
import subprocess
import sys
from pathlib import Path

SHIPPED_PREFIXES = ("app/", "templates/", "static/", "installer/")
SKIP_LABEL = "skip-changelog"
CHANGELOG = "CHANGELOG.md"


def needs_entry(changed_files: list[str]) -> bool:
    return any(path.startswith(SHIPPED_PREFIXES) for path in changed_files)


def unreleased_entries(changelog: str) -> set[str]:
    """Return the non-blank, non-heading lines in the [Unreleased] section."""
    entries: set[str] = set()
    inside = False
    for line in changelog.splitlines():
        if line.startswith("## "):
            inside = line.lower().startswith("## [unreleased]")
            continue
        stripped = line.strip()
        if inside and stripped and not stripped.startswith("#"):
            entries.add(stripped)
    return entries


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/master", help="git ref to compare against")
    parser.add_argument("--labels", default="", help="comma-separated pull request labels")
    args = parser.parse_args(argv)

    if SKIP_LABEL in {label.strip() for label in args.labels.split(",")}:
        print(f"changelog: skipped (label '{SKIP_LABEL}').")
        return 0

    merge_base = git("merge-base", args.base, "HEAD")
    if merge_base.returncode != 0:
        print(f"changelog: cannot find merge base with {args.base}.", file=sys.stderr)
        return 1
    base_sha = merge_base.stdout.strip()

    changed = git("diff", "--name-only", f"{base_sha}...HEAD").stdout.split()
    if not needs_entry(changed):
        print("changelog: OK (no shipped files changed).")
        return 0

    old = git("show", f"{base_sha}:{CHANGELOG}")
    old_entries = unreleased_entries(old.stdout) if old.returncode == 0 else set()
    new_entries = unreleased_entries(Path(CHANGELOG).read_text(encoding="utf-8"))
    if new_entries - old_entries:
        print("changelog: OK.")
        return 0

    print(
        f"changelog: files under {', '.join(SHIPPED_PREFIXES)} changed but {CHANGELOG} has no new "
        f"line under [Unreleased]. Add one, or label the PR '{SKIP_LABEL}'.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
