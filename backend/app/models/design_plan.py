from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class DesignPlan(Base):
    """设计方案模型 - AI 生成的美甲设计"""

    __tablename__ = "design_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)

    # AI 生成信息
    ai_prompt = Column(Text, nullable=False, comment="用于生成的AI提示词")
    generated_image_path = Column(String(500), nullable=False, comment="生成的设计图路径")
    model_version = Column(String(50), comment="使用的AI模型版本（如 dall-e-3）")

    # 设计参数
    design_target = Column(String(20), comment="设计目标（single/5nails/10nails）")
    style_keywords = Column(
        JSON,
        comment="风格关键词列表（JSON数组）"
    )

    # 参考图片
    reference_images = Column(
        JSON,
        comment="参考图片路径列表（JSON数组）"
    )

    # 版本控制（用于设计迭代）
    parent_design_id = Column(Integer, ForeignKey("design_plans.id"), nullable=True, comment="父设计方案ID（用于追踪迭代）")
    version = Column(Integer, default=1, comment="版本号")
    refinement_instruction = Column(Text, comment="迭代优化指令")

    # AI 估算信息
    estimated_duration = Column(Integer, comment="预估耗时（分钟）")
    estimated_materials = Column(
        JSON,
        comment="预估材料清单（JSON数组）"
    )
    difficulty_level = Column(String(20), comment="难度等级（简单/中等/困难）")

    # 其他信息
    title = Column(String(200), comment="设计方案标题")
    notes = Column(Text, comment="备注")
    is_archived = Column(Integer, default=0, comment="是否归档（1=是，0=否）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="design_plans")
    customer = relationship("Customer", back_populates="design_plans")
    service_records = relationship("ServiceRecord", back_populates="design_plan")

    # 自引用关系（设计迭代）
    parent_design = relationship("DesignPlan", remote_side=[id], backref="child_designs")

    def __repr__(self):
        return f"<DesignPlan(id={self.id}, title={self.title}, version={self.version})>"
