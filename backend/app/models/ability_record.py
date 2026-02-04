from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class AbilityRecord(Base):
    """能力记录模型 - 每次服务的技能评分记录"""

    __tablename__ = "ability_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_record_id = Column(Integer, ForeignKey("service_records.id", ondelete="CASCADE"), nullable=False, index=True)
    dimension_id = Column(Integer, ForeignKey("ability_dimensions.id"), nullable=False, index=True)

    # 评分信息
    score = Column(Integer, nullable=False, comment="评分（0-100）")
    evidence = Column(Text, comment="评分依据（AI 分析提取的证据）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # 关系
    user = relationship("User", back_populates="ability_records")
    service_record = relationship("ServiceRecord", back_populates="ability_records")
    dimension = relationship("AbilityDimension", back_populates="ability_records")

    def __repr__(self):
        return f"<AbilityRecord(id={self.id}, dimension_id={self.dimension_id}, score={self.score})>"
