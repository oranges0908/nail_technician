from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ==================== Customer Schemas ====================

class CustomerBase(BaseModel):
    """客户基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="客户姓名")
    phone: str = Field(..., min_length=11, max_length=20, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="电子邮件")
    avatar_path: Optional[str] = Field(None, max_length=500, description="头像路径")
    notes: Optional[str] = Field(None, description="备注")
    is_active: bool = Field(True, description="是否活跃")


class CustomerCreate(CustomerBase):
    """创建客户请求"""
    pass


class CustomerUpdate(BaseModel):
    """更新客户请求（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=11, max_length=20)
    email: Optional[EmailStr] = None
    avatar_path: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """客户响应"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Customer Profile Schemas ====================

class CustomerProfileBase(BaseModel):
    """客户档案基础 Schema"""
    # 指甲特征
    nail_shape: Optional[str] = Field(None, max_length=50, description="指甲形状")
    nail_length: Optional[str] = Field(None, max_length=50, description="指甲长度")
    nail_condition: Optional[str] = Field(None, description="指甲状况")
    nail_photos: Optional[List[str]] = Field(None, description="指甲照片路径列表")

    # 颜色偏好
    color_preferences: Optional[List[str]] = Field(None, description="喜欢的颜色")
    color_dislikes: Optional[List[str]] = Field(None, description="不喜欢的颜色")

    # 风格偏好
    style_preferences: Optional[List[str]] = Field(None, description="风格偏好")
    pattern_preferences: Optional[str] = Field(None, description="图案偏好")

    # 禁忌和限制
    allergies: Optional[str] = Field(None, description="过敏信息")
    prohibitions: Optional[str] = Field(None, description="禁忌事项")

    # 其他偏好
    occasion_preferences: Optional[dict] = Field(None, description="场合偏好")
    maintenance_preference: Optional[str] = Field(None, max_length=50, description="保养偏好")


class CustomerProfileCreate(CustomerProfileBase):
    """创建客户档案请求"""
    customer_id: int


class CustomerProfileUpdate(CustomerProfileBase):
    """更新客户档案请求（所有字段可选）"""
    pass


class CustomerProfileResponse(CustomerProfileBase):
    """客户档案响应"""
    id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Combined Schemas ====================

class CustomerWithProfile(CustomerResponse):
    """客户信息（含详细档案）"""
    profile: Optional[CustomerProfileResponse] = None

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    """客户列表响应"""
    total: int
    customers: List[CustomerResponse]
