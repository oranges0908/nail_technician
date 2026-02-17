# Stage 1: Build Flutter Web
FROM ghcr.io/cirruslabs/flutter:stable AS flutter-build

WORKDIR /app/frontend/nail_app
COPY frontend/nail_app/ .

RUN flutter pub get && \
    flutter build web --release --dart-define="API_BASE_URL=/api/v1"

# Stage 2: Runtime
FROM python:3.11-slim

# Install nginx and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy backend code and install dependencies
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy frontend build output to nginx
COPY --from=flutter-build /app/frontend/nail_app/build/web /usr/share/nginx/html

# Copy config files (nginx.conf as template for envsubst at runtime)
COPY nginx.conf /etc/nginx/nginx.conf.template
COPY supervisord.conf /app/supervisord.conf
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create directories for persistent data
RUN mkdir -p /app/backend/data /app/backend/uploads

# Default environment
ENV DATABASE_URL="sqlite:////app/backend/data/nail.db" \
    AI_PROVIDER="openai" \
    LOG_LEVEL="INFO"

# Railway uses $PORT; local Docker defaults to 80
EXPOSE ${PORT:-80}

ENTRYPOINT ["/app/docker-entrypoint.sh"]
