#!/usr/bin/env python
"""
简单的 API 测试脚本

用法：
    python test_api.py
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import Base, User, Customer, AbilityDimension
from datetime import date


def init_test_data(db: Session):
    """初始化测试数据"""

    print("🚀 初始化测试数据...")

    # 1. 创建测试用户
    user = db.query(User).first()
    if not user:
        user = User(
            email="test@example.com",
            username="test_artist",
            hashed_password="hashed_password_here",  # 实际应该使用密码哈希
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ 创建测试用户: {user.username} (ID: {user.id})")
    else:
        print(f"✅ 使用现有用户: {user.username} (ID: {user.id})")

    # 2. 创建测试客户
    customer = db.query(Customer).filter(Customer.user_id == user.id).first()
    if not customer:
        customer = Customer(
            user_id=user.id,
            name="张小美",
            phone="13800138000",
            notes="VIP客户，喜欢简约风格"
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        print(f"✅ 创建测试客户: {customer.name} (ID: {customer.id})")
    else:
        print(f"✅ 使用现有客户: {customer.name} (ID: {customer.id})")

    # 3. 创建能力维度
    dimensions = [
        ("颜色搭配", "color_matching", "评估色彩组合的和谐度和创意性"),
        ("图案精度", "pattern_precision", "评估图案的精确度和对称性"),
        ("细节处理", "detail_work", "评估边缘处理、亮片分布等细节"),
        ("整体构图", "composition", "评估整体布局和视觉平衡"),
        ("技法运用", "technique_application", "评估技法的熟练度和多样性"),
        ("创意表达", "creative_expression", "评估设计的原创性和艺术表现力")
    ]

    for name, name_en, desc in dimensions:
        dimension = db.query(AbilityDimension).filter(AbilityDimension.name == name).first()
        if not dimension:
            dimension = AbilityDimension(
                name=name,
                name_en=name_en,
                description=desc,
                is_active=1
            )
            db.add(dimension)

    db.commit()
    print(f"✅ 创建能力维度: 共 {len(dimensions)} 个")

    print("\n✨ 测试数据初始化完成！\n")
    return user, customer


def test_models():
    """测试数据库模型"""

    print("=" * 60)
    print("📊 测试数据库模型")
    print("=" * 60)

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user, customer = init_test_data(db)

        # 统计信息
        print("📈 数据库统计:")
        print(f"  - 用户数: {db.query(User).count()}")
        print(f"  - 客户数: {db.query(Customer).count()}")
        print(f"  - 能力维度数: {db.query(AbilityDimension).count()}")

        print("\n✅ 数据库模型测试通过！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

    return True


def test_import():
    """测试模块导入"""

    print("=" * 60)
    print("📦 测试模块导入")
    print("=" * 60)

    try:
        # 测试导入所有关键模块
        from app.models import (
            User, Customer, CustomerProfile,
            DesignPlan, ServiceRecord, ComparisonResult,
            AbilityDimension, AbilityRecord, InspirationImage
        )
        print("✅ 模型导入成功")

        from app.schemas.service import (
            ServiceRecordCreate, ServiceRecordComplete, ServiceRecordResponse
        )
        print("✅ Schema 导入成功")

        from app.services.ai.factory import AIProviderFactory
        print("✅ AI Provider 工厂导入成功")

        from app.services.service_record_service import ServiceRecordService
        from app.services.analysis_service import AnalysisService
        print("✅ 业务服务导入成功")

        from app.api.v1 import services
        print("✅ API 路由导入成功")

        print("\n✅ 所有模块导入测试通过！")
        return True

    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""

    print("\n")
    print("🧪 " + "=" * 56 + " 🧪")
    print("   Nail 美甲师能力成长系统 - API 测试")
    print("🧪 " + "=" * 56 + " 🧪")
    print("\n")

    # 测试1: 模块导入
    if not test_import():
        print("\n❌ 模块导入测试失败，退出")
        sys.exit(1)

    print("\n")

    # 测试2: 数据库模型
    if not test_models():
        print("\n❌ 数据库模型测试失败，退出")
        sys.exit(1)

    print("\n")
    print("=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print("\n")
    print("📝 下一步:")
    print("  1. 启动服务: uvicorn app.main:app --reload")
    print("  2. 访问 API 文档: http://localhost:8000/docs")
    print("  3. 测试 API 端点")
    print("\n")


if __name__ == "__main__":
    main()
