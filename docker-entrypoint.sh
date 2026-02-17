#!/bin/bash
set -e

# Create data and upload directories (all under /app/backend/data for single volume mount)
mkdir -p /app/backend/data
mkdir -p /app/backend/data/uploads/nails
mkdir -p /app/backend/data/uploads/inspirations
mkdir -p /app/backend/data/uploads/designs
mkdir -p /app/backend/data/uploads/actuals

# Run database migrations
cd /app/backend
DATABASE_URL="sqlite:////app/backend/data/nail.db" alembic upgrade head

# Railway provides $PORT; default to 80 for local Docker
APP_PORT="${PORT:-80}"
echo "==> Starting uvicorn on 0.0.0.0:${APP_PORT}"

exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}" --proxy-headers --forwarded-allow-ips='*'
