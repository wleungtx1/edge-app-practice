# CLAUDE.md

Practice repo for the GitHub workflow (personal account `wleungtx1`, private). It mirrors the
layout, tooling and CI of a production repo but contains only toy code.

## Rules

- Never commit, push or tag until the user confirms that specific action.
- Stage files by explicit path — no `git add -A`, `git add .` or whole folders.
- Default branch is `master`; work on branches and merge through pull requests.
- LF line endings everywhere (`.gitattributes` enforces it; Python file writers use `newline="\n"`).
- No real product code, company names, credentials, keys or customer data in this repo.
- Shell: PowerShell 5.1 strips quotes in native args — use the Bash tool or files for JSON and
  `gh` bodies.

## Conventions

- Python 3.11, black + ruff (line length 100), mypy strict, pytest (`asyncio_mode = "auto"`).
- Coverage floor 88 % overall, 95 % for `app/config.py` and `app/database.py`, 90 % on changed lines.
- `app/database.py` `MIGRATIONS` is append-only.
- Any change under `app/`, `templates/`, `static/` or `installer/` needs a line under
  `## [Unreleased]` in `CHANGELOG.md` (or the PR label `skip-changelog`).
- `docs/` holds only the allowlisted user-facing documents (see `scripts/checks/docs_allowlist.py`);
  planning notes go in `local-doc/` (git-ignored).
- Release = tag `vX.Y.Z` matching `__version__` in `app/__init__.py`.
