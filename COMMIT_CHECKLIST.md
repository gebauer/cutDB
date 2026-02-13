# Pre-commit checklist (GitHub)

Use this before pushing to GitHub and deploying from the repo.

## Already configured

- **Secrets**: No secrets in tracked files. `SECRET_KEY` and DB credentials come from env (`template_settings.py`). `local_settings.py` is gitignored.
- **.gitignore**: Ignores `.env`, `db.sqlite3`, `staticfiles/`, `local_settings.py`, `database_dump/dump.sql`, `database_dump/dump_sqlite.sql`, and other local/generated files.
- **.dockerignore**: Keeps Docker build context small (no `.git`, `.env`, dumps, `__pycache__`, etc.).

## Before first push

1. **Do not commit** (they are ignored):
   - `cutDB/settings/local_settings.py`
   - `.env`
   - `db.sqlite3`
   - `database_dump/dump.sql` and `database_dump/dump_sqlite.sql`

2. **Commit and push**:
   - All code under `cutDB/`, `database/` (except ignored files)
   - `manage.py`, `pyproject.toml`, `poetry.lock`
   - `Dockerfile`, `docker-entrypoint.sh`, `.dockerignore`
   - `README.md`, `DEPLOYMENT.md`, `PLAN.md`, `.env.example`
   - `database_dump/README.md`, `database_dump/mysql_dump_to_sqlite.py`

3. **Optional**: If you want the SQL dump in the repo (e.g. for new clones), remove `database_dump/dump.sql` from `.gitignore`. Note: the dump contains an auth user (email + password hash); prefer keeping it out of the repo and copying it to the server separately.

## Deploy from GitHub (Coolify)

1. In Coolify, create an application from your **GitHub repository**.
2. Build: **Dockerfile** at repo root.
3. Set env vars (see `DEPLOYMENT.md`); mount volume at `/data` for SQLite.
4. Deploy. Copy `db.sqlite3` to `/data/db.sqlite3` on the server if you use existing data.
