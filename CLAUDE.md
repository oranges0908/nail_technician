# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nail** is an AI-powered nail artist capability growth system built with **Flutter** (frontend) and **FastAPI** (backend). The system helps nail artists generate personalized design plans using AI, track service records, and analyze their skill development over time through AI-driven comparison and feedback.

### Core Business Features

1. **Customer Management**: Maintain detailed customer profiles including nail characteristics, style preferences, and service history
2. **AI Design Generation**: Generate personalized nail art designs based on customer profiles and inspiration images using DALL-E 3
3. **Design Refinement**: Iteratively refine designs using GPT-4 Vision with natural language instructions
4. **Service Tracking**: Record actual service results with photos and duration
5. **AI-Powered Analysis**: Compare design plans vs actual results using GPT-4 Vision to identify differences
6. **Capability Tracking**: Build skill radar charts across dimensions like color matching, pattern precision, detail work, etc.

### Technology Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL/MySQL + Redis
- **Frontend**: Flutter (cross-platform mobile app)
- **AI**: OpenAI API (DALL-E 3 for generation, GPT-4 Vision for analysis)
- **Storage**: Local filesystem for MVP (images stored in `uploads/` directory)

## Architecture

### Backend Layered Architecture

The backend follows a strict **layered architecture** with AI abstraction:

```
API Routes → Services (Business Logic) → AI Provider Layer → External AI APIs
                ↓
          ORM Models → Database
```

**Key architectural principles:**

1. **AI Provider Abstraction**: All AI calls go through an abstract `AIProvider` interface, making it easy to swap OpenAI for other providers (Baidu, Alibaba, etc.)
2. **Dependency Injection**: Database sessions and AI providers injected via FastAPI's `Depends()`
3. **Versioned APIs**: All routes under `/api/v1` prefix for future compatibility
4. **Pydantic Settings**: Configuration loaded from `.env` via `app.core.config.Settings`
5. **Factory Pattern**: `AIProviderFactory` creates AI provider instances based on configuration

### AI Provider Architecture (Critical Pattern)

```python
# app/services/ai/base.py - Abstract interface
class AIProvider(ABC):
    async def generate_design(prompt, reference_images, design_target) -> str
    async def refine_design(original_image, refinement_instruction) -> str
    async def estimate_execution(design_image) -> Dict
    async def compare_images(design_image, actual_image) -> Dict

# app/services/ai/openai_provider.py - OpenAI implementation
class OpenAIProvider(AIProvider):
    # Implements all methods using DALL-E 3 and GPT-4 Vision

# app/services/ai/factory.py - Factory for provider creation
class AIProviderFactory:
    @classmethod
    def get_provider(provider_type: str) -> AIProvider
```

**Business services use the factory** instead of calling OpenAI directly:

```python
# app/services/design_service.py
ai_provider = AIProviderFactory.get_provider()
design_url = await ai_provider.generate_design(prompt, images)
```

This allows switching AI providers by changing `AI_PROVIDER` in `.env` without touching business logic.

### Domain Model Overview

**Core entities:**

- `User`: Nail artist account
- `Customer`: Customer profile with basic info
- `CustomerProfile`: Detailed nail characteristics, color preferences, style preferences, prohibitions
- `InspirationImage`: Reference images uploaded by nail artist, tagged for search
- `DesignPlan`: AI-generated design with prompt, image path, estimated duration/materials, version tracking
- `ServiceRecord`: Actual service performed, links design plan to actual result photo
- `ComparisonResult`: AI analysis comparing design vs actual (similarity score, differences, suggestions)
- `AbilityDimension`: Skill dimensions (color matching, pattern precision, etc.)
- `AbilityRecord`: Per-service skill scores extracted from AI analysis

**Key relationships:**

- Design plans can have `parent_design_id` for tracking refinement iterations
- Service records link `design_plan_id` → `actual_image_path` → `comparison_result`
- Comparison results generate `ability_records` across multiple dimensions

### File Storage Structure

Images are stored locally in `backend/uploads/`:

```
uploads/
├── nails/          # Customer nail profile photos
├── inspirations/   # Reference/inspiration images
├── designs/        # AI-generated design images
└── actuals/        # Actual service completion photos
```

FastAPI serves these via static file mounting at `/uploads`.

## Common Commands

### Backend Development

**Initial setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# IMPORTANT: Edit .env and add your OPENAI_API_KEY
```

**Run backend (development):**
```bash
cd backend
uvicorn app.main:app --reload
# OR
python -m app.main
```

**Run with Docker Compose (PostgreSQL + Redis + Backend):**
```bash
docker-compose up -d
docker-compose logs -f backend  # View logs
docker-compose down  # Stop all services
```

**Database migrations (Alembic):**
```bash
cd backend
# First time setup (if alembic/ doesn't exist)
alembic init alembic

# After modifying models in app/models/
alembic revision --autogenerate -m "description of changes"
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

**Testing:**
```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_main.py # Specific file
pytest -k "test_name"     # Specific test
```

**Code quality:**
```bash
cd backend
black .                   # Format code
flake8                    # Lint
mypy app                  # Type checking
```

### Frontend Development

**Setup (first time):**
```bash
cd frontend
flutter create nail_app
cd nail_app
# Copy pubspec_template.yaml contents to pubspec.yaml
flutter pub get
```

**Run app:**
```bash
cd frontend/nail_app
flutter devices                # List available devices
flutter run                    # Run on default device
flutter run -d <device_id>     # Run on specific device
```

**Code generation (required for JSON serialization):**
```bash
cd frontend/nail_app
flutter pub run build_runner build
flutter pub run build_runner build --delete-conflicting-outputs  # Force rebuild
flutter pub run build_runner watch  # Auto-rebuild on changes
```

**Testing:**
```bash
cd frontend/nail_app
flutter test
flutter test --coverage
flutter test test/models/user_test.dart  # Specific file
```

**Build for release:**
```bash
flutter build apk --release       # Android APK
flutter build appbundle --release # Android App Bundle
flutter build ios --release       # iOS (requires macOS)
```

## Development Workflows

### Adding a New Backend Feature (Example: Customer Management)

1. **Create SQLAlchemy model** in `backend/app/models/customer.py`:
   ```python
   from app.db.database import Base
   from sqlalchemy import Column, Integer, String, ForeignKey

   class Customer(Base):
       __tablename__ = "customers"
       id = Column(Integer, primary_key=True, index=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       name = Column(String(100), nullable=False)
   ```

2. **Import model** in `backend/app/models/__init__.py`:
   ```python
   from app.models.customer import Customer
   ```

3. **Create Pydantic schemas** in `backend/app/schemas/customer.py`:
   ```python
   from pydantic import BaseModel

   class CustomerCreate(BaseModel):
       name: str
       phone: str | None = None

   class CustomerResponse(BaseModel):
       id: int
       name: str
       phone: str | None

       model_config = {"from_attributes": True}
   ```

4. **Create service** in `backend/app/services/customer_service.py`:
   ```python
   from sqlalchemy.orm import Session
   from app.models.customer import Customer

   class CustomerService:
       @staticmethod
       def create_customer(db: Session, customer_data: dict, user_id: int):
           customer = Customer(**customer_data, user_id=user_id)
           db.add(customer)
           db.commit()
           db.refresh(customer)
           return customer
   ```

5. **Create API route** in `backend/app/api/v1/customers.py`:
   ```python
   from fastapi import APIRouter, Depends
   from app.db.database import get_db
   from app.schemas.customer import CustomerCreate, CustomerResponse
   from app.services.customer_service import CustomerService

   router = APIRouter()

   @router.post("/", response_model=CustomerResponse)
   async def create_customer(
       customer: CustomerCreate,
       db: Session = Depends(get_db)
   ):
       return CustomerService.create_customer(db, customer.dict(), user_id=1)
   ```

6. **Register router** in `backend/app/api/v1/__init__.py`:
   ```python
   from app.api.v1 import customers
   api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
   ```

7. **Run migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "add customer model"
   alembic upgrade head
   ```

8. **Test the endpoint:**
   - Visit http://localhost:8000/docs
   - Or write tests in `backend/tests/test_customers.py`

### Adding AI Functionality (Example: Design Generation)

When adding AI features, **always use the AI provider abstraction**:

```python
# app/services/design_service.py
from app.services.ai.factory import AIProviderFactory

class DesignService:
    @staticmethod
    async def generate_design(customer_profile: dict, inspiration_images: List[str]):
        # Build AI prompt from customer profile
        prompt = f"Generate nail art design with {customer_profile['color_preferences']}"

        # Get AI provider (configured in .env)
        ai_provider = AIProviderFactory.get_provider()

        # Generate design
        design_url = await ai_provider.generate_design(
            prompt=prompt,
            reference_images=inspiration_images,
            design_target="10nails"  # single/5nails/10nails
        )

        # Save to database
        design_plan = DesignPlan(
            ai_prompt=prompt,
            generated_image_path=design_url,
            ...
        )
        return design_plan
```

**Never call OpenAI directly** - always go through `AIProviderFactory.get_provider()`.

### Adding a New Frontend Feature

1. **Define model** in `lib/models/customer.dart`:
   ```dart
   import 'package:json_annotation/json_annotation.dart';
   part 'customer.g.dart';

   @JsonSerializable()
   class Customer {
     final int id;
     final String name;
     final String? phone;

     Customer({required this.id, required this.name, this.phone});

     factory Customer.fromJson(Map<String, dynamic> json) => _$CustomerFromJson(json);
     Map<String, dynamic> toJson() => _$CustomerToJson(this);
   }
   ```

2. **Run code generator:**
   ```bash
   flutter pub run build_runner build
   ```

3. **Create API service** in `lib/services/customer_service.dart`:
   ```dart
   import 'package:dio/dio.dart';
   import '../models/customer.dart';

   class CustomerService {
     final Dio dio;
     CustomerService(this.dio);

     Future<Customer> createCustomer(Map<String, dynamic> data) async {
       final response = await dio.post('/customers', data: data);
       return Customer.fromJson(response.data);
     }
   }
   ```

4. **Create provider** in `lib/providers/customer_provider.dart`:
   ```dart
   import 'package:flutter/foundation.dart';
   import '../services/customer_service.dart';

   class CustomerProvider extends ChangeNotifier {
     List<Customer> _customers = [];

     Future<void> addCustomer(Map<String, dynamic> data) async {
       final customer = await CustomerService.createCustomer(data);
       _customers.add(customer);
       notifyListeners();
     }
   }
   ```

5. **Build UI** in `lib/screens/customer/customer_list_screen.dart`

6. **Register provider** in `lib/main.dart`:
   ```dart
   MultiProvider(
     providers: [
       ChangeNotifierProvider(create: (_) => CustomerProvider()),
     ],
     child: MyApp(),
   )
   ```

## Important Configuration

### Environment Variables (.env)

**Required for development:**

```bash
# Database - Use SQLite for quick start
DATABASE_URL=sqlite:///./nail.db

# OR use PostgreSQL (recommended for production)
DATABASE_URL=postgresql://nail_user:nail_password@localhost:5432/nail_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT - CHANGE IN PRODUCTION
SECRET_KEY=your-secret-key-change-in-production-use-secrets-token-hex

# AI Provider (REQUIRED for AI features)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here

# CORS - Adjust for your Flutter app
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

**AI Provider Configuration:**

- Set `AI_PROVIDER=openai` to use OpenAI (DALL-E 3 + GPT-4 Vision)
- Future: `AI_PROVIDER=baidu` for Baidu AI (requires implementation)
- **MUST set `OPENAI_API_KEY`** for AI features to work

### Database Configuration

**SQLite (default, for quick development):**
```bash
DATABASE_URL=sqlite:///./nail.db
```
- No setup required
- Data stored in `backend/nail.db` file
- Not recommended for production

**PostgreSQL (recommended):**
```bash
# Using docker-compose
docker-compose up -d postgres
DATABASE_URL=postgresql://nail_user:nail_password@localhost:5432/nail_db
```

**MySQL (alternative):**
```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/nail_db
```

### File Upload Configuration

Files are stored in `backend/uploads/` with subdirectories:

```python
# app/core/config.py
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = 10485760  # 10MB

# Directory structure created automatically:
# uploads/nails/          - Customer nail photos
# uploads/inspirations/   - Reference images
# uploads/designs/        - AI-generated designs
# uploads/actuals/        - Service completion photos
```

Static files served at `http://localhost:8000/uploads/<subdirectory>/<filename>`.

## API Documentation

- **Swagger UI**: http://localhost:8000/docs (interactive API docs)
- **ReDoc**: http://localhost:8000/redoc (alternative docs)
- **Health Check**: http://localhost:8000/health or http://localhost:8000/api/v1/health

All business endpoints are under `/api/v1` prefix.

## Key Architectural Patterns

### 1. AI Provider Abstraction

**Why**: To support multiple AI providers (OpenAI, Baidu, etc.) without changing business logic.

**How**: All AI calls go through `AIProviderFactory.get_provider()` which returns an `AIProvider` interface.

**Where**:
- Interface: `app/services/ai/base.py`
- OpenAI implementation: `app/services/ai/openai_provider.py`
- Factory: `app/services/ai/factory.py`

### 2. Dependency Injection

**Database sessions**:
```python
@router.get("/customers/{id}")
async def get_customer(id: int, db: Session = Depends(get_db)):
    # db is automatically injected
```

**Current user** (from JWT):
```python
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    # current_user extracted from JWT token
```

### 3. Pydantic Settings

All configuration in `app/core/config.py` using `pydantic_settings.BaseSettings`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"  # Automatically loads from .env
```

Access via `from app.core.config import settings`.

### 4. ORM Model Registration

**Critical**: After creating/modifying models in `app/models/`, import them in `app/models/__init__.py`:

```python
# app/models/__init__.py
from app.models.user import User
from app.models.customer import Customer
from app.models.design_plan import DesignPlan
# ... import all models here
```

This ensures Alembic can detect schema changes for migrations.

### 5. Router Registration

All API routers must be registered in `app/api/v1/__init__.py`:

```python
from app.api.v1 import auth, users, customers, designs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
# ... register all routers
```

## Testing

### Backend Testing (pytest)

```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose
pytest --cov=app          # With coverage
pytest -k "customer"      # Tests matching "customer"
```

**Test structure**:
```python
# tests/test_customers.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_customer():
    response = client.post("/api/v1/customers", json={"name": "Test"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

### Frontend Testing (Flutter)

```bash
cd frontend/nail_app
flutter test
flutter test --coverage
```

## File Naming Conventions

- **Backend (Python)**: `snake_case` for files, functions, variables
- **Frontend (Dart)**: `snake_case` for files, `camelCase` for variables/functions, `PascalCase` for classes
- **Models**: Singular names (e.g., `user.py`, `customer.dart`, not `users.py`)
- **API routes**: Plural resource names (e.g., `/customers`, `/designs`)

## Current Implementation Status

**Implemented:**
- ✅ Backend project structure with FastAPI
- ✅ Configuration management with Pydantic Settings
- ✅ Database setup with SQLAlchemy (supports PostgreSQL, MySQL, SQLite)
- ✅ User model and schemas (template)
- ✅ API route stubs (auth, users, health) - return 501 Not Implemented
- ✅ Docker Compose configuration (PostgreSQL + Redis + Backend)
- ✅ File upload directory structure

**Not Yet Implemented (needs development):**
- ⏳ AI provider layer (`app/services/ai/`) - base.py, openai_provider.py, factory.py
- ⏳ Domain models (Customer, CustomerProfile, DesignPlan, ServiceRecord, ComparisonResult, etc.)
- ⏳ Business service layer (customer_service.py, design_service.py, analysis_service.py)
- ⏳ Actual API route implementations (currently stubs)
- ⏳ JWT authentication logic (token generation/validation)
- ⏳ Database migrations with Alembic (needs `alembic init alembic`)
- ⏳ Flutter project (needs `flutter create nail_app`)
- ⏳ Frontend-backend integration

## Reference Documentation

- **Business Requirements**: `docs/BUSINESS.md` - Detailed feature descriptions and user stories
- **Architecture Details**: `docs/ARCHITECTURE.md` - Deep dive into system architecture, AI provider design, database schema
- **API Specifications**: `docs/API.md` - API endpoint details
- **Setup Guide**: `docs/SETUP.md` - Deployment and production setup
- **Project Structure**: `PROJECT_STRUCTURE.md` - Directory structure overview
- **Flutter Structure**: `frontend/flutter_structure.md` - Flutter app organization

## Common Issues and Solutions

**Issue: Alembic can't detect model changes**
- **Solution**: Ensure model is imported in `app/models/__init__.py`

**Issue: AI features return errors**
- **Solution**: Check that `OPENAI_API_KEY` is set in `.env` and `AI_PROVIDER=openai`

**Issue: CORS errors from Flutter app**
- **Solution**: Add Flutter dev server URL to `ALLOWED_ORIGINS` in `.env`

**Issue: Database connection errors**
- **Solution**: If using PostgreSQL/MySQL, ensure database server is running (or use `docker-compose up -d`)

**Issue: Flutter JSON serialization errors**
- **Solution**: Run `flutter pub run build_runner build` after modifying models

**Issue: File upload fails**
- **Solution**: Check that `uploads/` directory exists and has write permissions
