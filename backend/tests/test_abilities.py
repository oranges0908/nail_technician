"""
能力维度相关功能测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.ability_dimension import AbilityDimension
from app.models.ability_record import AbilityRecord
from app.models.service_record import ServiceRecord
from app.services.ability_service import AbilityService


# 测试数据库（使用内存数据库）
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_abilities.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="test_password",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_customer(db, test_user):
    """创建测试客户"""
    customer = Customer(
        user_id=test_user.id,
        name="测试客户",
        phone="13800138000",
        is_active=1
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def test_initialize_dimensions(db):
    """测试初始化能力维度"""
    # 第一次初始化
    created_count = AbilityService.initialize_dimensions(db)
    assert created_count == 6

    # 验证维度已创建
    dimensions = db.query(AbilityDimension).all()
    assert len(dimensions) == 6

    # 验证维度名称
    dimension_names = {d.name for d in dimensions}
    expected_names = {"颜色搭配", "图案精度", "细节处理", "整体构图", "技法运用", "创意表达"}
    assert dimension_names == expected_names

    # 第二次初始化（幂等性测试）
    created_count = AbilityService.initialize_dimensions(db)
    assert created_count == 0

    # 确认没有重复
    dimensions = db.query(AbilityDimension).all()
    assert len(dimensions) == 6


def test_list_dimensions(db):
    """测试列出维度"""
    # 初始化维度
    AbilityService.initialize_dimensions(db)

    # 列出所有启用的维度
    dimensions = AbilityService.list_dimensions(db, include_inactive=False)
    assert len(dimensions) == 6

    # 按 display_order 排序
    assert dimensions[0].display_order <= dimensions[1].display_order


def test_get_dimension_by_name(db):
    """测试根据名称获取维度"""
    # 初始化维度
    AbilityService.initialize_dimensions(db)

    # 获取存在的维度
    dimension = AbilityService.get_dimension_by_name(db, "颜色搭配")
    assert dimension is not None
    assert dimension.name == "颜色搭配"
    assert dimension.name_en == "color_matching"

    # 获取不存在的维度
    dimension = AbilityService.get_dimension_by_name(db, "不存在的维度")
    assert dimension is None


def test_get_ability_stats(db, test_user, test_customer):
    """测试获取能力统计"""
    # 初始化维度
    AbilityService.initialize_dimensions(db)
    dimensions = db.query(AbilityDimension).all()

    # 创建测试服务记录
    service = ServiceRecord(
        user_id=test_user.id,
        customer_id=test_customer.id,
        service_date=date(2026, 2, 1),
        status="completed"
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    # 创建能力记录
    for i, dimension in enumerate(dimensions):
        record = AbilityRecord(
            user_id=test_user.id,
            service_record_id=service.id,
            dimension_id=dimension.id,
            score=70 + i * 5  # 70, 75, 80, 85, 90, 95
        )
        db.add(record)
    db.commit()

    # 获取统计
    stats = AbilityService.get_ability_stats(db, test_user.id)

    assert len(stats["dimensions"]) == 6
    assert len(stats["scores"]) == 6
    assert stats["total_records"] == 6
    assert 70 <= stats["avg_score"] <= 95


def test_get_ability_summary(db, test_user, test_customer):
    """测试获取能力总结"""
    # 初始化维度
    AbilityService.initialize_dimensions(db)
    dimensions = db.query(AbilityDimension).all()

    # 创建测试服务记录
    service = ServiceRecord(
        user_id=test_user.id,
        customer_id=test_customer.id,
        service_date=date(2026, 2, 1),
        status="completed"
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    # 创建能力记录（不同的分数）
    scores = [60, 70, 80, 85, 90, 95]
    for dimension, score in zip(dimensions, scores):
        record = AbilityRecord(
            user_id=test_user.id,
            service_record_id=service.id,
            dimension_id=dimension.id,
            score=score
        )
        db.add(record)
    db.commit()

    # 获取总结
    summary = AbilityService.get_ability_summary(db, test_user.id)

    # 验证擅长的维度（前3名）
    assert len(summary["strengths"]) == 3
    assert summary["strengths"][0]["score"] >= summary["strengths"][1]["score"]
    assert summary["strengths"][1]["score"] >= summary["strengths"][2]["score"]

    # 验证待提升的维度（后3名）
    assert len(summary["improvements"]) == 3
    assert summary["improvements"][0]["score"] <= summary["improvements"][1]["score"]
    assert summary["improvements"][1]["score"] <= summary["improvements"][2]["score"]


def test_get_ability_trend(db, test_user, test_customer):
    """测试获取能力趋势"""
    # 初始化维度
    AbilityService.initialize_dimensions(db)
    dimension = db.query(AbilityDimension).filter(
        AbilityDimension.name == "颜色搭配"
    ).first()

    # 创建多个服务记录和能力记录
    for i in range(5):
        service = ServiceRecord(
            user_id=test_user.id,
            customer_id=test_customer.id,
            service_date=date(2026, 2, i+1),
            status="completed"
        )
        db.add(service)
        db.commit()
        db.refresh(service)

        record = AbilityRecord(
            user_id=test_user.id,
            service_record_id=service.id,
            dimension_id=dimension.id,
            score=60 + i * 5  # 60, 65, 70, 75, 80
        )
        db.add(record)
    db.commit()

    # 获取趋势
    trend = AbilityService.get_ability_trend(db, test_user.id, "颜色搭配", limit=10)

    assert trend["dimension_name"] == "颜色搭配"
    assert len(trend["data_points"]) == 5

    # 验证按时间升序排列
    scores = [point["score"] for point in trend["data_points"]]
    assert scores == [60, 65, 70, 75, 80]


# API 端点测试（需要认证，暂时跳过）
# 可以在集成测试中添加
