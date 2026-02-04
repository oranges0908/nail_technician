# 导入所有模型，确保 Alembic 能够检测到
from app.db.database import Base

# 导入所有模型（Alembic 需要）
from app.models.user import User
from app.models.customer import Customer
from app.models.customer_profile import CustomerProfile
from app.models.inspiration_image import InspirationImage
from app.models.design_plan import DesignPlan
from app.models.service_record import ServiceRecord
from app.models.comparison_result import ComparisonResult
from app.models.ability_dimension import AbilityDimension
from app.models.ability_record import AbilityRecord

__all__ = [
    "Base",
    "User",
    "Customer",
    "CustomerProfile",
    "InspirationImage",
    "DesignPlan",
    "ServiceRecord",
    "ComparisonResult",
    "AbilityDimension",
    "AbilityRecord",
]
