# Deploying CutDB (CeColDB) with Coolify

Production URL: **https://CeColDB.xcience.net**

## Requirements

- Coolify instance with Docker build support
- Git repo connected (GitHub/GitLab or public repo URL)

## Environment variables (set in Coolify)

Set these in your Coolify application **Environment Variables**:

| Variable | Required | Example | Notes |
|----------|----------|---------|--------|
| `DJANGO_SECRET_KEY` | **Yes** | (long random string) | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG` | Yes | `0` | Use `0` in production. |
| `ALLOWED_HOSTS` | Yes | `CeColDB.xcience.net,localhost,127.0.0.1` | Comma-separated. Include `localhost` for Coolify health checks. |
| `DB_NAME` | Recommended | `/data/db.sqlite3` | Path to SQLite file. Use `/data/db.sqlite3` and mount a volume at `/data` (see below). |
| `STATIC_ROOT` | Optional | `/app/staticfiles` | Default is fine; static files are collected at build time. |
| `CLUSTALO_BIN` | Optional | (empty or path) | Leave unset to disable alignment; or install Clustal Omega in the image and set path. |

## SQLite database

You can **copy your existing `db.sqlite3`** into the server:

1. **Option A – Coolify persistent storage (recommended)**  
   - In Coolify, add a **Persistent Storage** volume for the application: mount path **`/data`**.  
   - Set env **`DB_NAME=/data/db.sqlite3`**.  
   - After first deploy, open a shell (or use “Execute Command”) and upload/copy your `db.sqlite3` into `/data/db.sqlite3`. The entrypoint runs `migrate` on startup, so the DB will be created if missing or updated if you copied an existing one.

2. **Option B – Bake into image**  
   - Copy `db.sqlite3` into the project root before building and add `COPY db.sqlite3 /data/db.sqlite3` in the Dockerfile (and ensure `/data` exists). Less flexible for updates.

3. **Option C – Empty DB**  
   - Use only `DB_NAME=/data/db.sqlite3` and a `/data` volume. On first run, migrations create an empty DB; then use Django admin or imports to add data.

## Coolify setup

1. **New Application** → Source: your Git repository.  
2. **Build**  
   - Build Pack: **Dockerfile**.  
   - Dockerfile path: `Dockerfile` (repo root).  
3. **Port**: `8000`.  
4. **Domain**: `CeColDB.xcience.net` (Coolify will proxy and can add TLS).  
5. **Environment**: Add the variables from the table above.  
6. **Persistent storage** (for SQLite): Add volume, container path **`/data`**.  
7. Deploy. The container runs `migrate` then **gunicorn** on port 8000.

## First deploy with your existing data

1. Deploy once so the app and volume exist.  
2. Copy your local `db.sqlite3` to the server (e.g. `scp db.sqlite3 user@server:/path/to/coolify/data/...` or use Coolify’s file/shell to place it at `/data/db.sqlite3` in the container).  
3. Restart the application so it uses the new DB.

## Optional: Clustal Omega in Docker

If you want alignments in production, install Clustal Omega in the image and set `CLUSTALO_BIN`:

```dockerfile
# In Dockerfile after poetry install, add:
RUN apt-get update && apt-get install -y --no-install-recommends clustalomega \
    && rm -rf /var/lib/apt/lists/*
ENV CLUSTALO_BIN=/usr/bin/clustalo
```

(Adjust package name for your base image; Debian uses `clustalomega`.)

## Checklist

- [ ] `DJANGO_SECRET_KEY` set (random, secret)  
- [ ] `DJANGO_DEBUG=0`  
- [ ] `ALLOWED_HOSTS=CeColDB.xcience.net,localhost,127.0.0.1`  
- [ ] Volume mounted at `/data`, `DB_NAME=/data/db.sqlite3`  
- [ ] `db.sqlite3` copied to `/data/` in container if using existing data  
