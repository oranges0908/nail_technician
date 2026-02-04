from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class ComparisonResult(Base):
    """对比分析结果模型 - 存储 AI 对比设计图和实际图的分析结果"""

    __tablename__ = "comparison_results"

    id = Column(Integer, primary_key=True, index=True)
    service_record_id = Column(
        Integer,
        ForeignKey("service_records.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="关联的服务记录ID"
    )

    # 分析结果
    similarity_score = Column(Integer, nullable=False, comment="相似度评分（0-100）")
    differences = Column(JSON, comment="差异分析（JSON）")
    suggestions = Column(JSON, comment="改进建议（JSON数组）")

    # 新增：基于复盘和反馈的上下文洞察
    contextual_insights = Column(
        JSON,
        comment="基于复盘和反馈的上下文洞察（JSON）"
    )

    # 时间戳
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # 关系
    service_record = relationship("ServiceRecord", back_populates="comparison_result")

    def __repr__(self):
        return f"<ComparisonResult(id={self.id}, service_record_id={self.service_record_id}, similarity={self.similarity_score})>"
