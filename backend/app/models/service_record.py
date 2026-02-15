from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class ServiceRecord(Base):
    """服务记录模型 - 记录实际美甲服务的完成情况"""

    __tablename__ = "service_records"

    # 基础字段
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    design_plan_id = Column(Integer, ForeignKey("design_plans.id"), nullable=True, index=True)

    # 服务基本信息
    service_date = Column(Date, nullable=False, index=True, comment="服务日期")
    service_duration = Column(Integer, comment="服务时长（分钟）")
    actual_image_path = Column(String(500), comment="实际完成图路径")

    # 新增：材料和复盘字段
    materials_used = Column(Text, comment="实际使用的材料清单（自由文本）")
    artist_review = Column(Text, comment="美甲师复盘内容")
    customer_feedback = Column(Text, comment="客户反馈")
    customer_satisfaction = Column(Integer, comment="客户满意度评分（1-5星）")

    # 其他信息
    notes = Column(Text, comment="其他备注")
    status = Column(String(20), default="pending", comment="状态: pending/completed")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="service_records")
    customer = relationship("Customer", back_populates="service_records")
    design_plan = relationship("DesignPlan", back_populates="service_records")
    comparison_result = relationship(
        "ComparisonResult",
        back_populates="service_record",
        uselist=False,
        cascade="all, delete-orphan"
    )
    ability_records = relationship(
        "AbilityRecord",
        back_populates="service_record",
        cascade="all, delete-orphan"
    )

    @property
    def design_image_path(self):
        """从关联的设计方案获取设计图路径"""
        if self.design_plan and self.design_plan.generated_image_path:
            return self.design_plan.generated_image_path
        return None

    def __repr__(self):
        return f"<ServiceRecord(id={self.id}, customer_id={self.customer_id}, date={self.service_date}, status={self.status})>"
