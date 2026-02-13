# CutDB

CutDB is a database application for analysing cuticular collagens from *C. elegans*.

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- [Clustal Omega](http://www.clustal.org/omega/) binary (path set in settings)

The app uses **SQLite** by default (no separate database server). The DB file is created at `db.sqlite3` in the project root.

## Installation (Poetry)

1. **Install Poetry** (if needed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:

   ```bash
   cd /path/to/CutDB
   poetry install
   ```

3. **Local settings**  
   Copy the template settings to your local settings and adjust:

   ```bash
   cp cutDB/settings/template_settings.py cutDB/settings/local_settings.py
   ```

   Edit `cutDB/settings/local_settings.py` and set at least:

   - `SECRET_KEY` (or set env `DJANGO_SECRET_KEY`)
   - `CLUSTALO_BIN`: full path to the Clustal Omega executable (if you use alignment features)

   Optional: copy `.env.example` to `.env` and set variables there; the template reads `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `ALLOWED_HOSTS`, `CLUSTALO_BIN`, `STATIC_ROOT`. SQLite is used by default (no DB credentials).

4. **Database**  
   Run migrations (creates `db.sqlite3` in the project root):

   ```bash
   poetry run python manage.py migrate --settings=cutDB.settings.local_settings
   ```

5. **Run the development server**:

   ```bash
   poetry run python manage.py runserver --settings=cutDB.settings.local_settings
   ```

   Open http://127.0.0.1:8000/ (or http://127.0.0.1:8000/database/ depending on your URL config).

## Legacy pip install (not recommended)

Previously, dependencies were installed with pip (including mysqlclient). The project now uses **SQLite** and **Poetry**; see `pyproject.toml` and run `poetry install`.

The project now uses Poetry; see `pyproject.toml` and run `poetry install` instead.

## Deployment (Coolify)

See [PLAN.md](PLAN.md) for Phase 2: Docker + Coolify deployment (after Phase 1: Poetry and local run).
