from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础 Schema"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, max_length=100, description="密码（至少6位）")
    invite_code: str = Field(..., description="邀请码")


class UserUpdate(BaseModel):
    """更新用户请求（所有字段可选）"""
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserPasswordUpdate(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码（至少6位）")


class UserResponse(UserBase):
    """用户响应（不包含密码）"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """数据库中的用户（包含密码哈希）"""
    hashed_password: str

    model_config = {"from_attributes": True}
