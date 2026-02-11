"""
集成测试共享 fixtures — 复用主 conftest 的基础设施，提供业务流程级别的 helpers
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db


# 独立的内存 SQLite 引擎（与单元测试隔离）
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """每个测试函数独立的数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """TestClient，覆盖 get_db 依赖"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---- Mock AI Provider ----

MOCK_GENERATED_IMAGE = "https://example.com/generated_design.png"
MOCK_REFINED_IMAGE = "https://example.com/refined_design.png"
MOCK_ESTIMATION = {
    "estimated_duration": 60,
    "difficulty_level": "中等",
    "materials": ["基础底胶", "彩色甲油", "亮片"],
    "techniques": ["渐变", "彩绘"],
}
MOCK_COMPARISON = {
    "similarity_score": 85,
    "overall_assessment": "完成度高，色彩还原准确",
    "differences": {
        "color_accuracy": "颜色基本准确，渐变过渡自然",
        "pattern_precision": "图案线条清晰",
    },
    "suggestions": ["可以更注意边缘细节", "渐变可以更平滑"],
    "contextual_insights": {
        "artist_skill_level": "中高级",
        "improvement_areas": ["边缘处理"],
    },
    "ability_scores": {
        "颜色搭配": {"score": 88, "evidence": "色彩搭配和谐，渐变自然"},
        "图案精度": {"score": 85, "evidence": "图案线条清晰，对称性好"},
        "细节处理": {"score": 80, "evidence": "边缘处理尚可，亮片分布均匀"},
        "整体构图": {"score": 90, "evidence": "整体布局美观，视觉平衡"},
        "技法运用": {"score": 82, "evidence": "渐变技法熟练"},
        "创意表达": {"score": 87, "evidence": "设计有创意"},
    },
}


def _mock_ai_provider():
    """创建 mock AI provider 实例"""
    mock_provider = AsyncMock()
    mock_provider.generate_design.return_value = MOCK_GENERATED_IMAGE
    mock_provider.refine_design.return_value = MOCK_REFINED_IMAGE
    mock_provider.estimate_execution.return_value = MOCK_ESTIMATION
    mock_provider.compare_images.return_value = MOCK_COMPARISON
    return mock_provider


@pytest.fixture
def mock_ai():
    """Mock AI Provider — 用 context manager 返回 patch 对象"""
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock:
        mock.return_value = _mock_ai_provider()
        yield mock
