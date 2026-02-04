from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class CustomerProfile(Base):
    """客户详细档案模型 - 存储美甲特征、偏好等详细信息"""

    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # 指甲特征
    nail_shape = Column(String(50), comment="指甲形状（椭圆/方形/圆形/杏仁形等）")
    nail_length = Column(String(50), comment="指甲长度（短/中/长）")
    nail_condition = Column(Text, comment="指甲状况描述（质地、健康状况等）")
    nail_photos = Column(
        JSON,
        comment="指甲照片路径列表（JSON数组）"
    )

    # 颜色偏好
    color_preferences = Column(
        JSON,
        comment="喜欢的颜色列表（JSON数组）"
    )
    color_dislikes = Column(
        JSON,
        comment="不喜欢的颜色列表（JSON数组）"
    )

    # 风格偏好
    style_preferences = Column(
        JSON,
        comment="喜欢的风格标签（简约/华丽/可爱/性感等，JSON数组）"
    )
    pattern_preferences = Column(Text, comment="图案偏好描述")

    # 禁忌和限制
    allergies = Column(Text, comment="过敏信息")
    prohibitions = Column(Text, comment="禁忌事项（不能接受的元素、颜色等）")

    # 其他偏好
    occasion_preferences = Column(
        JSON,
        comment="场合偏好（日常/职场/派对/婚礼等，JSON对象）"
    )
    maintenance_preference = Column(String(50), comment="保养偏好（持久性/易维护/快速等）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    customer = relationship("Customer", back_populates="profile")

    def __repr__(self):
        return f"<CustomerProfile(id={self.id}, customer_id={self.customer_id})>"
