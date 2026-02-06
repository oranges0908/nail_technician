"""
能力分析完整流程测试
测试 AI 对比分析 → 能力记录提取 → 能力统计/趋势
"""
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.design_plan import DesignPlan
from app.models.service_record import ServiceRecord
from app.models.comparison_result import ComparisonResult
from app.models.ability_dimension import AbilityDimension
from app.models.ability_record import AbilityRecord
from app.services.analysis_service import AnalysisService
from app.services.ability_service import AbilityService


# 测试数据库（使用内存数据库）
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ability_analysis.db"
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
def test_user(db):
    """创建测试用户"""
    user = User(
        email="analyst@example.com",
        username="analyst",
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
        name="分析测试客户",
        phone="13900139000",
        is_active=1
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def test_dimensions(db):
    """初始化能力维度"""
    AbilityService.initialize_dimensions(db)
    return db.query(AbilityDimension).all()


@pytest.fixture
def test_design_plan(db, test_user):
    """创建测试设计方案"""
    design = DesignPlan(
        user_id=test_user.id,
        ai_prompt="优雅粉色渐变美甲",
        generated_image_path="test_design.png",
        estimated_duration=60
    )
    db.add(design)
    db.commit()
    db.refresh(design)
    return design


@pytest.fixture
def test_service_record(db, test_user, test_customer, test_design_plan):
    """创建测试服务记录"""
    service = ServiceRecord(
        user_id=test_user.id,
        customer_id=test_customer.id,
        design_plan_id=test_design_plan.id,
        service_date=date(2026, 2, 5),
        actual_image_path="test_actual.png",
        artist_review="整体完成度不错，但时间稍紧张，渐变部分有待提升",
        customer_feedback="很满意，颜色很漂亮！",
        customer_satisfaction=5,
        status="completed"
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


# Mock AI 响应数据
MOCK_AI_COMPARISON_RESULT = {
    "similarity_score": 88,
    "overall_assessment": "整体完成度高，颜色还原准确，细节处理优秀",
    "differences": {
        "color_accuracy": "颜色还原度90%，渐变过渡自然",
        "pattern_precision": "图案精度85%，线条流畅",
        "detail_work": "细节处理完整，亮片分布均匀",
        "composition": "整体构图协调，与设计方案一致"
    },
    "contextual_insights": {
        "artist_perspective": "美甲师提到时间紧张，但完成度仍然很高，展现了良好的时间管理能力",
        "customer_perspective": "客户反馈与视觉分析一致，5星评分反映了高满意度",
        "satisfaction_analysis": "视觉效果与客户满意度高度匹配"
    },
    "suggestions": [
        "渐变过渡可以更加细腻",
        "预留更充足时间以提升细节质量"
    ],
    "ability_scores": {
        "颜色搭配": {"score": 90, "evidence": "粉色渐变自然，色彩组合协调"},
        "图案精度": {"score": 85, "evidence": "线条清晰，图案规整"},
        "细节处理": {"score": 88, "evidence": "亮片分布均匀，边缘处理细致"},
        "整体构图": {"score": 87, "evidence": "布局合理，视觉平衡"},
        "技法运用": {"score": 86, "evidence": "渐变技法熟练"},
        "创意表达": {"score": 82, "evidence": "忠实还原设计方案"}
    }
}


@pytest.mark.asyncio
async def test_full_analysis_pipeline(
    db,
    test_user,
    test_customer,
    test_dimensions,
    test_service_record
):
    """
    测试完整的能力分析流程：
    1. AI 对比分析（Mock）
    2. 提取能力评分
    3. 保存能力记录
    4. 验证能力记录正确性
    """

    # Mock AI Provider 的 compare_images 方法
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.compare_images.return_value = MOCK_AI_COMPARISON_RESULT
        mock_factory.return_value = mock_provider

        # 执行分析
        comparison_result = await AnalysisService.analyze_service(
            db=db,
            service_record_id=test_service_record.id
        )

        # 验证对比结果已保存
        assert comparison_result is not None
        assert comparison_result.similarity_score == 88
        assert "渐变过渡可以更加细腻" in comparison_result.suggestions

        # 验证能力记录已创建
        ability_records = db.query(AbilityRecord).filter(
            AbilityRecord.service_record_id == test_service_record.id
        ).all()

        assert len(ability_records) == 6  # 6 个维度

        # 验证各维度评分
        score_map = {record.dimension.name: record.score for record in ability_records}
        assert score_map["颜色搭配"] == 90
        assert score_map["图案精度"] == 85
        assert score_map["细节处理"] == 88
        assert score_map["整体构图"] == 87
        assert score_map["技法运用"] == 86
        assert score_map["创意表达"] == 82

        # 验证证据已保存
        color_record = next(r for r in ability_records if r.dimension.name == "颜色搭配")
        assert "粉色渐变自然" in color_record.evidence


@pytest.mark.asyncio
async def test_ability_stats_after_analysis(
    db,
    test_user,
    test_dimensions,
    test_service_record
):
    """测试分析后的能力统计功能"""

    # Mock AI 分析
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.compare_images.return_value = MOCK_AI_COMPARISON_RESULT
        mock_factory.return_value = mock_provider

        # 执行分析
        await AnalysisService.analyze_service(db=db, service_record_id=test_service_record.id)

        # 获取能力统计
        stats = AbilityService.get_ability_stats(db, test_user.id)

        assert len(stats["dimensions"]) == 6
        assert len(stats["scores"]) == 6
        assert stats["total_records"] == 6

        # 验证平均分在合理范围内
        assert 82 <= stats["avg_score"] <= 90

        # 验证各维度分数
        dimension_score_map = dict(zip(stats["dimensions"], stats["scores"]))
        assert dimension_score_map["颜色搭配"] == 90
        assert dimension_score_map["图案精度"] == 85


@pytest.mark.asyncio
async def test_ability_summary_after_analysis(
    db,
    test_user,
    test_dimensions,
    test_service_record
):
    """测试分析后的能力总结功能"""

    # Mock AI 分析
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.compare_images.return_value = MOCK_AI_COMPARISON_RESULT
        mock_factory.return_value = mock_provider

        # 执行分析
        await AnalysisService.analyze_service(db=db, service_record_id=test_service_record.id)

        # 获取能力总结
        summary = AbilityService.get_ability_summary(db, test_user.id)

        # 验证擅长维度（前3名）
        assert len(summary["strengths"]) == 3
        assert summary["strengths"][0]["dimension"] == "颜色搭配"  # 90分，最高
        assert summary["strengths"][0]["score"] == 90

        # 验证待提升维度（后3名，升序排列）
        assert len(summary["improvements"]) == 3
        assert summary["improvements"][0]["dimension"] == "创意表达"  # 82分，最低
        assert summary["improvements"][0]["score"] == 82

        # 验证服务次数
        assert summary["total_services"] == 1


@pytest.mark.asyncio
async def test_ability_trend_after_multiple_services(
    db,
    test_user,
    test_customer,
    test_design_plan,
    test_dimensions
):
    """测试多次服务后的能力成长趋势"""

    # Mock AI 分析
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock_factory:
        mock_provider = AsyncMock()

        # 创建 3 次服务记录，模拟能力提升
        scores_progression = [
            {"颜色搭配": 75, "图案精度": 70, "细节处理": 72, "整体构图": 74, "技法运用": 71, "创意表达": 68},
            {"颜色搭配": 82, "图案精度": 78, "细节处理": 80, "整体构图": 81, "技法运用": 79, "创意表达": 75},
            {"颜色搭配": 90, "图案精度": 85, "细节处理": 88, "整体构图": 87, "技法运用": 86, "创意表达": 82}
        ]

        for i, scores in enumerate(scores_progression):
            # 创建服务记录
            service = ServiceRecord(
                user_id=test_user.id,
                customer_id=test_customer.id,
                design_plan_id=test_design_plan.id,
                service_date=date(2026, 2, i+1),
                actual_image_path=f"test_actual_{i}.png",
                status="completed"
            )
            db.add(service)
            db.commit()
            db.refresh(service)

            # Mock AI 响应（不同的评分）
            mock_result = MOCK_AI_COMPARISON_RESULT.copy()
            mock_result["ability_scores"] = {
                dim: {"score": score, "evidence": f"第{i+1}次服务评分"}
                for dim, score in scores.items()
            }
            mock_provider.compare_images.return_value = mock_result
            mock_factory.return_value = mock_provider

            # 执行分析
            await AnalysisService.analyze_service(db=db, service_record_id=service.id)

        # 获取颜色搭配的成长趋势
        trend = AbilityService.get_ability_trend(db, test_user.id, "颜色搭配", limit=10)

        assert trend["dimension_name"] == "颜色搭配"
        assert len(trend["data_points"]) == 3

        # 验证成长趋势（按时间升序）
        scores = [point["score"] for point in trend["data_points"]]
        assert scores == [75, 82, 90]  # 能力提升


@pytest.mark.asyncio
async def test_reanalysis_updates_ability_records(
    db,
    test_user,
    test_dimensions,
    test_service_record
):
    """测试重新分析时能力记录会被正确更新"""

    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock_factory:
        mock_provider = AsyncMock()

        # 第一次分析
        mock_provider.compare_images.return_value = MOCK_AI_COMPARISON_RESULT
        mock_factory.return_value = mock_provider

        await AnalysisService.analyze_service(db=db, service_record_id=test_service_record.id)

        # 验证初始记录数
        initial_count = db.query(AbilityRecord).filter(
            AbilityRecord.service_record_id == test_service_record.id
        ).count()
        assert initial_count == 6

        # 第二次分析（修改后的评分）
        updated_result = MOCK_AI_COMPARISON_RESULT.copy()
        updated_result["ability_scores"]["颜色搭配"]["score"] = 95  # 提升评分
        mock_provider.compare_images.return_value = updated_result

        await AnalysisService.analyze_service(db=db, service_record_id=test_service_record.id)

        # 验证记录数未增加（旧记录被删除）
        final_count = db.query(AbilityRecord).filter(
            AbilityRecord.service_record_id == test_service_record.id
        ).count()
        assert final_count == 6

        # 验证评分已更新
        color_record = db.query(AbilityRecord).join(AbilityDimension).filter(
            AbilityRecord.service_record_id == test_service_record.id,
            AbilityDimension.name == "颜色搭配"
        ).first()
        assert color_record.score == 95


def test_ability_records_cascade_delete(
    db,
    test_user,
    test_customer,
    test_design_plan,
    test_dimensions
):
    """测试删除服务记录时能力记录会级联删除"""

    # 创建服务记录
    service = ServiceRecord(
        user_id=test_user.id,
        customer_id=test_customer.id,
        design_plan_id=test_design_plan.id,
        service_date=date(2026, 2, 5),
        actual_image_path="test.png",
        status="completed"
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    # 手动创建能力记录
    for dimension in test_dimensions:
        record = AbilityRecord(
            user_id=test_user.id,
            service_record_id=service.id,
            dimension_id=dimension.id,
            score=80
        )
        db.add(record)
    db.commit()

    # 验证记录已创建
    assert db.query(AbilityRecord).filter(
        AbilityRecord.service_record_id == service.id
    ).count() == 6

    # 删除服务记录
    db.delete(service)
    db.commit()

    # 验证能力记录已级联删除
    assert db.query(AbilityRecord).filter(
        AbilityRecord.service_record_id == service.id
    ).count() == 0
