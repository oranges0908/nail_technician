"""
共享 pytest fixtures — 为所有测试提供数据库会话、TestClient、认证等基础设施
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.core.security import hash_password


# 内存 SQLite，所有测试共享同一引擎但每个函数独立事务
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """每个测试函数独立的数据库会话（create_all → yield → drop_all）"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """TestClient，覆盖 get_db 依赖注入为测试 db_session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """测试用户的原始数据"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "test123456"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """通过 API 注册用户，返回响应 JSON"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, test_user_data, registered_user):
    """登录并返回认证 headers: {"Authorization": "Bearer <token>"}"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_tokens(client, test_user_data, registered_user):
    """登录并返回完整 token 信息（含 refresh_token）"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        }
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def test_customer(client, auth_headers):
    """通过 API 创建测试客户，返回响应 JSON"""
    response = client.post(
        "/api/v1/customers/",
        json={
            "name": "测试客户",
            "phone": "13800138000",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


# ---- 第二用户 fixtures（用于数据隔离测试）----

@pytest.fixture
def second_user_data():
    """第二个测试用户的原始数据"""
    return {
        "email": "second@example.com",
        "username": "seconduser",
        "password": "second123456"
    }


@pytest.fixture
def second_auth_headers(client, second_user_data):
    """第二用户：注册+登录，返回认证 headers"""
    client.post("/api/v1/auth/register", json=second_user_data)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": second_user_data["email"],
            "password": second_user_data["password"],
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---- 灵感图 fixtures ----

@pytest.fixture
def test_inspiration(client, auth_headers):
    """通过 API 创建测试灵感图，返回响应 JSON"""
    response = client.post(
        "/api/v1/inspirations/",
        json={
            "image_path": "/uploads/inspirations/test.jpg",
            "title": "测试灵感图",
            "description": "一个测试用的灵感图",
            "tags": ["渐变", "粉色"],
            "category": "渐变",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


# ---- 设计 fixtures ----

MOCK_GENERATED_IMAGE = "https://example.com/generated_design.png"
MOCK_ESTIMATION = {
    "estimated_duration": 60,
    "difficulty_level": "中等",
    "materials": ["基础底胶", "彩色甲油", "亮片"],
    "techniques": ["渐变", "彩绘"],
}


def _mock_ai_provider():
    """创建 mock AI provider 实例"""
    mock_provider = AsyncMock()
    mock_provider.generate_design.return_value = MOCK_GENERATED_IMAGE
    mock_provider.refine_design.return_value = "https://example.com/refined_design.png"
    mock_provider.estimate_execution.return_value = MOCK_ESTIMATION
    mock_provider.compare_images.return_value = {
        "similarity_score": 85,
        "overall_assessment": "完成度高",
        "differences": {"color_accuracy": "颜色准确"},
        "suggestions": ["可以更细致"],
        "contextual_insights": {},
        "ability_scores": {
            "颜色搭配": {"score": 88, "evidence": "色彩协调"},
            "图案精度": {"score": 85, "evidence": "图案清晰"},
        },
    }
    return mock_provider


@pytest.fixture
def test_design(client, auth_headers):
    """通过 API 创建测试设计方案（mock AI），返回响应 JSON"""
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock:
        mock.return_value = _mock_ai_provider()
        response = client.post(
            "/api/v1/designs/generate",
            json={"prompt": "测试提示词", "title": "测试设计"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        return response.json()


# ---- 服务记录 fixtures ----

@pytest.fixture
def test_service_record(client, auth_headers, test_customer, test_design):
    """通过 API 创建测试服务记录，返回响应 JSON"""
    response = client.post(
        "/api/v1/services/",
        json={
            "customer_id": test_customer["id"],
            "design_plan_id": test_design["id"],
            "service_date": "2025-01-15",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()
