from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime


class Customer(Base):
    """客户基本信息模型"""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="所属美甲师ID")

    # 基本信息
    name = Column(String(100), nullable=False, index=True, comment="客户姓名")
    phone = Column(String(20), unique=True, index=True, comment="联系电话")
    email = Column(String(100), comment="电子邮件")
    avatar_path = Column(String(500), comment="客户头像路径")

    # 其他信息
    notes = Column(Text, comment="备注")
    is_active = Column(Integer, default=1, comment="是否活跃（1=是，0=否）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="customers")
    profile = relationship("CustomerProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    service_records = relationship("ServiceRecord", back_populates="customer", cascade="all, delete-orphan")
    design_plans = relationship("DesignPlan", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, phone={self.phone})>"
