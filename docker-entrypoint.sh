#!/bin/bash
set -e

# Create data and upload directories
mkdir -p /app/backend/data
mkdir -p /app/backend/uploads/nails
mkdir -p /app/backend/uploads/inspirations
mkdir -p /app/backend/uploads/designs
mkdir -p /app/backend/uploads/actuals

# Railway provides $PORT; default to 80 for local Docker
export NGINX_PORT="${PORT:-80}"
echo "==> Railway PORT=$PORT, NGINX_PORT=$NGINX_PORT"

# Substitute env vars in nginx config template
envsubst '${NGINX_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
echo "==> nginx listen config:"
grep 'listen' /etc/nginx/nginx.conf

# Run database migrations
cd /app/backend
DATABASE_URL="sqlite:////app/backend/data/nail.db" alembic upgrade head

# Start supervisord
exec supervisord -c /app/supervisord.conf
