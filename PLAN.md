# CutDB modernization plan

## Current state

- **Stack**: Django 1.11.3 (2017), no formal dependency file (README lists pip installs).
- **Dependencies**: django, django-tinymce, django-mathfilters, django-colorful, biopython, numpy, cython, requests (from management commands). **Database**: SQLite (no mysqlclient).
- **Settings**: `cutDB/settings/base.py` + `template_settings.py` (intended to be copied to `local_settings.py`; `local_settings.py` is gitignored). WSGI defaults to `cutDB.settings.template_settings`.
- **Database**: SQLite (ENGINE django.db.backends.sqlite3, file at project root).
- **External binary**: ClustalO (path set in local_settings as `CLUSTALO_BIN`).
- **Issues**:
  - No `requirements.txt` or `pyproject.toml` → dependencies not reproducible.
  - Django 1.11 is EOL and insecure; Python 2-era patterns in places.
  - `database/models.py`: uses deprecated `get_query_set()` (should be `get_queryset()`).
  - `database/urls.py`: uses deprecated `django.conf.urls.url` (Django 4.0+ prefers `re_path`); main app uses `cutDB/urls.py` with `re_path` (no include of `database.urls`).
  - Django 4.0: `USE_L10N` is removed (replaced by USE_L10N behavior by default).
  - Admin is in INSTALLED_APPS but not mounted in `cutDB/urls.py` (optional to add later).

---

## Phase 1: Switch to Poetry and run locally

**Goal**: Manage dependencies with Poetry and run the app locally (no Coolify yet).

1. **Add Poetry and lockfile**
   - Create `pyproject.toml` with:
     - Python `^3.10` (or `>=3.10,<3.13`).
     - Django `^4.2` (LTS) or `^5.0`.
     - django-tinymce, django-mathfilters, django-colorful, biopython, numpy, cython, requests.
   - Run `poetry install` to generate `poetry.lock`.

2. **Settings and env**
   - Keep `base.py` and `template_settings.py`.
   - Add `.env.example` with: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `ALLOWED_HOSTS` (or document), optional `DB_NAME` (SQLite path), `CLUSTALO_BIN`, `STATIC_ROOT`.
   - Optionally: make settings load from env (e.g. `os.environ.get('DB_NAME', 'cutdb')`) so a single `local_settings.py` (or template) can be used without editing for local runs.
   - WSGI: use `cutDB.settings` and set `DJANGO_SETTINGS_MODULE` via env in production; for local, keep `--settings=cutDB.settings.local_settings` or use env in `manage.py` / `.env`.

3. **Django 4 compatibility**
   - Remove or replace `USE_L10N` in `base.py` (deprecated in Django 4.0).
   - Replace `get_query_set` with `get_queryset` in `database/models.py`.
   - In `database/urls.py`: replace `from django.conf.urls import url` and `url(...)` with `from django.urls import re_path` and `re_path(...)` (for consistency; main routes are in `cutDB/urls.py`).

4. **README**
   - Document: install Poetry, then `poetry install`, copy/adjust settings from template, set `CLUSTALO_BIN`, run migrations, `poetry run python manage.py runserver --settings=cutDB.settings.local_settings` (or equivalent with env).

5. **Verify locally**
   - `poetry install`, configure local_settings (or env), `migrate` (creates SQLite DB), `runserver`, open `/database/` (or `/`).

---

## Phase 2: Deploy with Coolify (later)

**Goal**: Auto-deploy from Git using Coolify (Docker-based).

1. **Docker**
   - Add a **Dockerfile** that:
     - Uses a Python 3.10+ image.
     - Installs dependencies via `poetry export -f requirements.txt` and `pip install -r requirements.txt`, or use `poetry install --no-dev` in the image.
     - Sets `DJANGO_SETTINGS_MODULE` (e.g. `cutDB.settings` or a `cutDB.settings.production` that reads from env).
     - Runs `collectstatic`, then **gunicorn** (or uWSGI) with the cutDB WSGI app.
   - Optionally: **docker-compose.yml** for local parity (app + ClustalO or stub). SQLite DB file can live in a volume if you need persistence.

2. **Production settings**
   - `ALLOWED_HOSTS` from env (Coolify needs `localhost` for health checks + your domain).
   - `SECRET_KEY`, `DEBUG`, DB credentials, `STATIC_ROOT`, `CLUSTALO_BIN` from env.
   - Serve static via WhiteNoise or Coolify’s static handling if applicable.

3. **Coolify**
   - New resource → connect repo (e.g. GitHub).
   - Build: **Dockerfile** (or Nixpacks if you prefer); set build context to repo root.
   - Env vars: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `ALLOWED_HOSTS`, `CLUSTALO_BIN`, etc. No DB credentials needed for SQLite; optionally set `DB_NAME` to a path in a persistent volume.
   - Pre/post deploy: run `migrate` (Coolify can run one-off commands or a small entrypoint script). For SQLite persistence across deploys, mount a volume for the directory containing `db.sqlite3`.

4. **ClustalO**
   - Ensure ClustalO is available in the container (install in Dockerfile or use a base image that includes it), and set `CLUSTALO_BIN` to the path inside the container.

---

## Summary

| Phase   | Focus                          | Outcome                          |
|---------|--------------------------------|-----------------------------------|
| Phase 1 | Poetry + run locally           | `poetry install`, runserver, app runs |
| Phase 2 | Coolify + Docker                | Git push → Coolify builds and deploys |

Phase 1 is done when the app runs locally under Poetry. Phase 2 is done when Coolify builds from the repo and the app responds on the configured domain.
