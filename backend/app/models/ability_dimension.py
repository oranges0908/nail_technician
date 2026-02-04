from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class AbilityDimension(Base):
    """能力维度模型 - 定义美甲师技能评估的各个维度"""

    __tablename__ = "ability_dimensions"

    id = Column(Integer, primary_key=True, index=True)

    # 维度信息
    name = Column(String(50), unique=True, nullable=False, index=True, comment="维度名称（如：颜色搭配）")
    name_en = Column(String(50), unique=True, comment="英文名称（如：color_matching）")
    description = Column(Text, comment="维度描述")

    # 评分标准
    scoring_criteria = Column(Text, comment="评分标准说明")

    # 显示顺序
    display_order = Column(Integer, default=0, comment="显示顺序")
    is_active = Column(Integer, default=1, comment="是否启用（1=是，0=否）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    ability_records = relationship("AbilityRecord", back_populates="dimension")

    def __repr__(self):
        return f"<AbilityDimension(id={self.id}, name={self.name})>"
