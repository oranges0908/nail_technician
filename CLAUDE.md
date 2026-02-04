# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nail is a cross-platform mobile application built with **Flutter** (frontend) and **FastAPI** (backend), with PostgreSQL/MySQL + Redis for data storage. The architecture follows a clean separation between frontend and backend, with each component in its own directory.

## Architecture

### Backend (FastAPI)

The backend follows a **layered architecture** pattern:

```
Models (SQLAlchemy) → Schemas (Pydantic) → Services (Business Logic) → API Routes
```

**Key architectural patterns:**
- All API routes are versioned under `/api/v1`
- Configuration is centralized in `backend/app/core/config.py` using Pydantic Settings that reads from `.env`
- Database session management uses dependency injection via `get_db()` from `backend/app/db/database.py`
- API router registration happens in `backend/app/api/v1/__init__.py` and is included in `main.py`
- Models inherit from SQLAlchemy's `Base` class defined in `backend/app/db/database.py`
- All API schemas use Pydantic v2 with `from_attributes = True` for ORM compatibility

**Authentication flow:**
- JWT-based authentication with access tokens (30 min) and refresh tokens (7 days)
- Token configuration in `app.core.config.Settings`
- Auth endpoints in `backend/app/api/v1/auth.py` (currently stubs)

### Frontend (Flutter)

The Flutter app (not yet created) follows a **feature-based architecture**:

```
Config → Models → Services (API) → Providers (State) → Screens/Widgets
```

**State management:** Provider pattern with `ChangeNotifierProvider`

**API communication:**
- Dio HTTP client with interceptors for JWT token injection
- Base URL configured in `lib/config/api_config.dart`
- Service layer handles all API calls

**Data flow:**
- Models use `json_serializable` for JSON serialization (requires code generation)
- API responses flow through services → providers → UI

## Common Commands

### Backend Development

**Setup and run:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**Run from Python:**
```bash
cd backend
python -m app.main
```

**Testing:**
```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_main.py # Run specific test file
```

**Code quality:**
```bash
cd backend
black .                   # Format code
flake8                    # Lint
mypy app                  # Type checking
```

**Database migrations:**
```bash
cd backend
alembic init alembic                           # First-time setup
alembic revision --autogenerate -m "message"   # Create migration
alembic upgrade head                           # Apply migrations
alembic downgrade -1                           # Rollback one version
```

**Important:** After creating or modifying models in `backend/app/models/`, ensure they are imported in `backend/app/models/__init__.py` so Alembic can detect them.

### Frontend Development

**Setup and run:**
```bash
cd frontend
flutter create nail_app
cd nail_app
# Copy contents from ../pubspec_template.yaml to pubspec.yaml
flutter pub get
flutter run
```

**Run on specific device:**
```bash
flutter devices           # List available devices
flutter run -d <device>   # Run on specific device
```

**Code generation (for JSON serialization):**
```bash
cd frontend/nail_app
flutter pub run build_runner build                 # One-time generation
flutter pub run build_runner build --delete-conflicting-outputs  # Force rebuild
flutter pub run build_runner watch                 # Watch mode
```

**Testing:**
```bash
cd frontend/nail_app
flutter test                    # Run all tests
flutter test test/models/       # Run specific directory
flutter test --coverage         # Generate coverage
```

**Build:**
```bash
flutter build apk --release       # Android APK
flutter build appbundle --release # Android App Bundle
flutter build ios --release       # iOS
```

### Docker

**Start all services (PostgreSQL, Redis, FastAPI):**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

**Rebuild and restart:**
```bash
docker-compose up -d --build
```

**Stop all services:**
```bash
docker-compose down
```

## Development Workflow

### Adding a New Backend Feature

1. **Create SQLAlchemy model** in `backend/app/models/` (inheriting from `Base`)
2. **Import model** in `backend/app/models/__init__.py`
3. **Create Pydantic schemas** in `backend/app/schemas/` (Create, Update, InDB variants)
4. **Implement business logic** in `backend/app/services/`
5. **Create API routes** in `backend/app/api/v1/`
6. **Register router** in `backend/app/api/v1/__init__.py`
7. **Run migration:** `alembic revision --autogenerate -m "description"`
8. **Apply migration:** `alembic upgrade head`
9. **Write tests** in `backend/tests/`

### Adding a New Frontend Feature

1. **Define model** in `lib/models/` with `@JsonSerializable()` annotation
2. **Run code generator:** `flutter pub run build_runner build`
3. **Create API service** in `lib/services/` using Dio
4. **Create provider** in `lib/providers/` extending `ChangeNotifier`
5. **Build UI** in `lib/screens/` and `lib/widgets/`
6. **Configure routes** in `lib/routes/app_router.dart`
7. **Test:** `flutter test`

## Important Notes

### Backend

- **Environment variables:** Always use `.env` for sensitive config (never commit `.env`)
- **Database URL:** Supports PostgreSQL, MySQL, and SQLite. SQLite is default for dev (`sqlite:///./nail.db`)
- **API versioning:** All endpoints are under `/api/v1` prefix
- **CORS:** Configured in `main.py`, defaults to allow all origins (tighten for production)
- **JWT secrets:** Change `SECRET_KEY` in production environment
- **File uploads:** Stored in `uploads/` directory (created automatically), max 10MB

### Frontend

- **Not yet created:** Run `flutter create nail_app` in `frontend/` directory first
- **Dependencies:** Reference `frontend/pubspec_template.yaml` for required packages
- **Code generation required:** Models using `json_serializable` need build_runner
- **API base URL:** Configure in `lib/config/api_config.dart` (default: `http://localhost:8000/api/v1`)
- **State management:** Provider pattern is configured, wrap providers in `main.dart`

### Database

- **PostgreSQL recommended** for production (see `docker-compose.yml`)
- **Redis** used for caching and session management
- **Migrations:** Alembic must be initialized with `alembic init alembic` on first use
- **Model changes:** Always create migration after modifying models

## API Documentation

- **Swagger UI:** http://localhost:8000/docs (auto-generated by FastAPI)
- **ReDoc:** http://localhost:8000/redoc (alternative documentation)
- **Health check:** http://localhost:8000/health or http://localhost:8000/api/v1/health

## File Naming Conventions

- **Backend:** Snake_case for all Python files and functions
- **Frontend:** Snake_case for Dart files, camelCase for variables/functions
- **Models:** Singular names (e.g., `user.py`, `user.dart`)
- **API routes:** Plural resource names (e.g., `/users`, `/items`)

## Testing

- **Backend:** Uses pytest with async support (`pytest-asyncio`)
- **Frontend:** Uses Flutter's built-in test framework
- **Integration tests:** Can use FastAPI's `TestClient` to test API without server

## Current Status

**Implemented:**
- Backend project structure with FastAPI
- User model and schemas (template)
- API route stubs for auth and users (endpoints return 501 Not Implemented)
- Database configuration with SQLAlchemy
- Docker setup with PostgreSQL and Redis
- Configuration management with Pydantic Settings

**Not yet implemented:**
- Flutter project (needs `flutter create nail_app`)
- Actual authentication logic (JWT generation/validation)
- Business logic in services layer
- Database migrations setup (need `alembic init`)
- User CRUD operations
- Frontend-backend integration

## Reference Documentation

- **API specs:** `docs/API.md`
- **Setup guide:** `docs/SETUP.md`
- **Project structure:** `PROJECT_STRUCTURE.md`
- **Flutter guide:** `frontend/flutter_structure.md`
