# Stage 1: Build Flutter Web
FROM ghcr.io/cirruslabs/flutter:stable AS flutter-build

WORKDIR /app/frontend/nail_app
COPY frontend/nail_app/ .

RUN flutter pub get && \
    flutter build web --release --dart-define="API_BASE_URL=/api/v1"

# Stage 2: Runtime (single-process uvicorn, no nginx/supervisor)
FROM python:3.11-slim

# Copy backend code and install dependencies
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy frontend build output (served by FastAPI)
COPY --from=flutter-build /app/frontend/nail_app/build/web /app/frontend/web

# Copy entrypoint
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create directories for persistent data
RUN mkdir -p /app/backend/data /app/backend/uploads

# Default environment
ENV DATABASE_URL="sqlite:////app/backend/data/nail.db" \
    AI_PROVIDER="openai" \
    LOG_LEVEL="INFO"

EXPOSE ${PORT:-80}

ENTRYPOINT ["/app/docker-entrypoint.sh"]
