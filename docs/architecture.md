# Architecture

A single FastAPI process with a SQLite database.

| Module | Role |
|---|---|
| `app/main.py` | `create_app()`: mounts routers, `/health` and the `/` page |
| `app/config.py` | `Settings` (pydantic-settings), read from `PRACTICE_*` env vars or `.env` |
| `app/database.py` | SQLite connection, `MIGRATIONS` (append-only) and `migrate()` |
| `app/routes/providers.py` | `/api/providers` CRUD |
| `templates/` | Jinja2 templates |

## Migrations

`MIGRATIONS` is a list of SQL statements. The database stores how many have been applied in
`schema_version`; on each connection `migrate()` applies the rest in order. A migration that has
reached `master` is never edited — add a new one at the end. CI enforces this with
`scripts/checks/migrations_append_only.py`.
