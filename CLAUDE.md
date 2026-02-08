# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nail** is an AI-powered nail artist capability growth system. Nail artists use it to generate personalized designs (DALL-E 3), track service records, and analyze skill development via AI comparison of designs vs actual results (GPT-4 Vision).

**Stack**: FastAPI backend + Flutter frontend + SQLAlchemy ORM + OpenAI API

## Common Commands

### Backend

```bash
# Run dev server (from backend/)
uvicorn app.main:app --reload

# Tests (from backend/)
pytest                         # all tests
pytest tests/test_main.py      # specific file
pytest -k "test_name"          # by name pattern
pytest test_customers.py       # root-level test files also exist

# Code quality (from backend/)
black .                        # format
flake8                         # lint
mypy app                       # type check

# Database migrations (from backend/)
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Frontend

```bash
# Run app (from frontend/nail_app/)
flutter run
flutter run -d <device_id>

# Code generation (required after modifying @JsonSerializable models)
flutter pub run build_runner build --delete-conflicting-outputs

# Tests (from frontend/nail_app/)
flutter test
flutter test test/models/user_test.dart
```

### Docker

```bash
docker-compose up -d           # PostgreSQL + Redis + Backend
docker-compose logs -f backend
```

## Architecture

### Backend: Layered Architecture

```
API Routes (app/api/v1/) → Services (app/services/) → AI Provider Layer (app/services/ai/)
                                    ↓
                           ORM Models (app/models/) → Database
```

- **Config**: `app/core/config.py` — Pydantic Settings loading from `.env`. Access via `from app.core.config import settings`
- **Auth**: JWT-based. `app/core/security.py` for token ops, `app/core/dependencies.py` for `get_current_user` / `get_current_active_user` injection
- **Database**: `app/db/database.py` — `get_db()` yields SQLAlchemy sessions, injected via `Depends(get_db)`
- **Exceptions**: Custom `NailAppException` in `app/core/exceptions.py`, with global handlers in `app/main.py`
- **Logging**: Structured logging via `app/core/logging_config.py` + request logging middleware

### AI Provider Abstraction (Critical Pattern)

All AI calls **must** go through the provider abstraction — never call OpenAI directly:

- `app/services/ai/base.py` — `AIProvider` ABC with methods: `generate_design`, `refine_design`, `estimate_execution`, `compare_images`
- `app/services/ai/openai_provider.py` — OpenAI implementation (DALL-E 3 + GPT-4 Vision)
- `app/services/ai/factory.py` — `AIProviderFactory.get_provider()` returns provider based on `AI_PROVIDER` env var

### Frontend: Provider Pattern

```
Screens (lib/screens/) → Providers (lib/providers/) → Services (lib/services/) → Backend API
                                                              ↑
                                                    Models (lib/models/) with @JsonSerializable
```

- **State management**: `provider` package with `ChangeNotifier` subclasses
- **Routing**: `go_router` configured in `lib/routes/app_router.dart`
- **API client**: `dio` configured in `lib/services/api_service.dart`
- **Auth flow**: `AuthProvider` initialized in `main()` and passed to `AppRouter` for route guards

### Key Domain Model Relationships

- `DesignPlan.parent_design_id` tracks refinement iterations (self-referential)
- `ServiceRecord` links a `DesignPlan` to an `actual_image_path`
- `ComparisonResult` links to a `ServiceRecord` and generates `AbilityRecord` entries across `AbilityDimension`s

## Critical Conventions

1. **New ORM models must be imported** in `backend/app/models/__init__.py` or Alembic won't detect them
2. **New API routers must be registered** in `backend/app/api/v1/__init__.py`
3. **After modifying Dart models** with `@JsonSerializable`, run `build_runner` to regenerate `.g.dart` files
4. **File naming**: Python uses `snake_case`; Dart uses `snake_case` for files, `PascalCase` for classes
5. **Model files**: singular (`user.py`, `customer.dart`); **API routes**: plural (`/customers`, `/designs`)
6. **Images** stored in `backend/uploads/` subdirectories: `nails/`, `inspirations/`, `designs/`, `actuals/` — served via static mount at `/uploads`
7. **All API routes** are under `/api/v1` prefix

## Environment Variables

Backend config via `backend/.env` (see `.env.example`). Key vars:

- `DATABASE_URL` — defaults to `sqlite:///./nail.db`; use PostgreSQL for production
- `OPENAI_API_KEY` — required for AI features
- `AI_PROVIDER` — `openai` (default); extensible to other providers
- `SECRET_KEY` — for JWT signing
- `ALLOWED_ORIGINS` — CORS origins for Flutter app

## Reference Docs

- `docs/BUSINESS.md` — Feature descriptions and user stories
- `docs/ARCHITECTURE.md` — System architecture and database schema
- `docs/API.md` — API endpoint specifications
- `docs/SETUP.md` — Deployment guide
