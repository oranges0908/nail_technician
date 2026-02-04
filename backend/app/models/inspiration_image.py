from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class InspirationImage(Base):
    """灵感图库模型 - 美甲师上传的参考图片"""

    __tablename__ = "inspiration_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="上传者ID")

    # 图片信息
    image_path = Column(String(500), nullable=False, comment="图片存储路径")
    title = Column(String(200), comment="图片标题")
    description = Column(Text, comment="图片描述")

    # 标签和分类（用于搜索和筛选）
    tags = Column(
        JSON,
        comment="标签列表（颜色/风格/图案等，JSON数组）"
    )
    category = Column(String(50), comment="分类（法式/渐变/贴片/彩绘等）")

    # 来源信息
    source_url = Column(String(500), comment="原始来源URL")
    source_platform = Column(String(50), comment="来源平台（小红书/Instagram等）")

    # 使用统计
    usage_count = Column(Integer, default=0, comment="被引用次数")
    last_used_at = Column(DateTime, comment="最后使用时间")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="inspiration_images")

    def __repr__(self):
        return f"<InspirationImage(id={self.id}, title={self.title}, category={self.category})>"
