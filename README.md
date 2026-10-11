# edge-app-practice

A sandbox for practising the GitHub workflow — pull requests, CI, branch protection and tagged
releases — on a tiny FastAPI app. The repo layout, tooling and checks mirror a larger production
repo so that everything proven here can be copied across.

## Setup (Python 3.11)

```bash
py -3.11 -m venv .venv                 # Windows; on Linux: python3.11 -m venv .venv
.venv/Scripts/activate                 # Linux: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install                     # after the first commit exists
uvicorn app.main:app --reload          # http://127.0.0.1:8000, API docs at /docs
```

## Everyday commands

| What | Command |
|---|---|
| Tests + coverage | `pytest --cov` |
| Lint / format / types | `ruff check .` · `black .` · `mypy app tests scripts` |
| All pre-commit hooks | `pre-commit run --all-files` |
| Project checks | `python scripts/checks/migrations_append_only.py` · `changelog_updated.py` · `docs_allowlist.py` |

## What CI enforces

**Linux job**: ruff, black, mypy (strict), pytest with coverage ≥ 88 %, critical modules
(`app/config.py`, `app/database.py`) ≥ 95 %, changed lines ≥ 90 % (diff-cover), pip-audit,
shellcheck, actionlint and the project checks in `scripts/checks/`.
**Windows job**: pytest and a stand-in `.msi` build.

## Releasing

1. Move the `[Unreleased]` entries in `CHANGELOG.md` under a new `## [X.Y.Z] - YYYY-MM-DD` heading
   and set `__version__` in `app/__init__.py` to `X.Y.Z` (via a PR).
2. After it merges: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. The Release workflow builds `EdgeApp-practice-X.Y.Z.run` and `.msi` with `.sha256` files and
   publishes a GitHub Release with all four attached.
