#!/bin/bash
set -e

# -------------------------------------------------------
# 路径规范化：将 .env 传入的相对路径转换为容器内绝对路径
# 确保 alembic 和 uvicorn 使用同一个数据库文件
# -------------------------------------------------------

# DATABASE_URL: 相对 SQLite 路径 → 容器绝对路径
case "${DATABASE_URL:-}" in
    sqlite:///./*)
        export DATABASE_URL="sqlite:////app/backend/data/nail.db"
        ;;
    "")
        export DATABASE_URL="sqlite:////app/backend/data/nail.db"
        ;;
esac

# UPLOAD_DIR: 相对路径 → 容器绝对路径（uploads 位于 /app/backend/data 卷下）
case "${UPLOAD_DIR:-}" in
    uploads|./uploads|uploads/)
        export UPLOAD_DIR="/app/backend/data/uploads"
        ;;
    "")
        export UPLOAD_DIR="/app/backend/data/uploads"
        ;;
esac

echo "==> DATABASE_URL=${DATABASE_URL}"
echo "==> UPLOAD_DIR=${UPLOAD_DIR}"

# Create data and upload directories (all under /app/backend/data for single volume mount)
mkdir -p /app/backend/data
mkdir -p "${UPLOAD_DIR}/nails"
mkdir -p "${UPLOAD_DIR}/inspirations"
mkdir -p "${UPLOAD_DIR}/designs"
mkdir -p "${UPLOAD_DIR}/actuals"

# Run database migrations
cd /app/backend
alembic upgrade head

# Railway provides $PORT; default to 80 for local Docker
APP_PORT="${PORT:-80}"
echo "==> Starting uvicorn on 0.0.0.0:${APP_PORT}"

exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}" --proxy-headers --forwarded-allow-ips='*'
