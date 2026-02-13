# Importing the SQL dump into local SQLite

The dump in `dump.sql` was exported from MariaDB/MySQL (HeidiSQL). To use it with your local SQLite database:

## 1. Create the schema (empty tables)

From the **project root** (where `manage.py` is):

```bash
poetry run python manage.py migrate --settings=cutDB.settings.local_settings
```

This creates `db.sqlite3` with the correct tables (empty).

## 2. Convert the dump to SQLite-compatible SQL

```bash
poetry run python database_dump/mysql_dump_to_sqlite.py
```

This reads `database_dump/dump.sql` and writes `database_dump/dump_sqlite.sql` (MySQL-specific syntax removed, backticks replaced for SQLite).

## 3. Load the data into SQLite

```bash
sqlite3 db.sqlite3 < database_dump/dump_sqlite.sql
```

(Or from the repo root: `sqlite3 db.sqlite3 < database_dump/dump_sqlite.sql`.)

## One-liner (after migrate)

```bash
poetry run python database_dump/mysql_dump_to_sqlite.py && sqlite3 db.sqlite3 < database_dump/dump_sqlite.sql
```

After that, run the app as usual; the DB will contain the dumped data (genes, clades, etc.). The dump includes an auth user; you can create a new superuser with `poetry run python manage.py createsuperuser` if needed.
