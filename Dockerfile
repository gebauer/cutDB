# CutDB / CeColDB - production image for Coolify
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=cutDB.settings.template_settings

WORKDIR /app

# Install system deps: Clustal Omega for sequence alignment
RUN apt-get update \
    && apt-get install -y --no-install-recommends clustalo \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and project dependencies
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-root

# Clustal Omega binary (override with env in Coolify if needed)
ENV CLUSTALO_BIN=/usr/bin/clustalo

# Application code
COPY manage.py ./
COPY cutDB ./cutDB
COPY database ./database
COPY docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

# Collect static files (WhiteNoise will serve them)
RUN python manage.py collectstatic --noinput

# Persistent data directory (mount a volume here for db.sqlite3)
RUN mkdir -p /data && chmod 777 /data

EXPOSE 8000

# Run migrations then gunicorn (DB_NAME should be /data/db.sqlite3 when using a volume)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "cutDB.wsgi:application"]
