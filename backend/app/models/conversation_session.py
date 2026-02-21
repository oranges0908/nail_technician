from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class ConversationSession(Base):
    """AI 对话会话模型"""

    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 会话状态：active | completed | abandoned
    status = Column(String(20), default="active", nullable=False)

    # 当前步骤名称：greeting | customer | design | service | complete | analysis | review
    current_step = Column(String(50), default="greeting", nullable=False)

    # 业务上下文 JSON，结构示例:
    # {
    #   "customer_id": 12, "customer_name": "王小花",
    #   "design_plan_id": 34, "service_record_id": 56,
    #   "comparison_result_id": 78, "inspiration_paths": [...]
    # }
    context = Column(JSON, default=dict)

    # 已完成步骤摘要列表，结构示例:
    # [{"step": "customer", "summary": "客户:王小花(ID:12)"}, ...]
    step_summaries = Column(JSON, default=list)

    # 本地 JSONL 对话文件路径
    file_path = Column(String(500))

    # 会话最终总结（会话结束时写入）
    summary = Column(Text)

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    completed_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User")

    def __repr__(self):
        return (
            f"<ConversationSession(id={self.id}, user_id={self.user_id}, "
            f"status={self.status}, step={self.current_step})>"
        )
