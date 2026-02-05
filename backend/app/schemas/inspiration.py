from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List


class InspirationImageBase(BaseModel):
    """灵感图基础 Schema"""
    title: Optional[str] = Field(None, max_length=200, description="图片标题")
    description: Optional[str] = Field(None, description="图片描述")
    tags: Optional[List[str]] = Field(None, description="标签列表（颜色/风格/图案等）")
    category: Optional[str] = Field(None, max_length=50, description="分类（法式/渐变/贴片/彩绘等）")
    source_url: Optional[str] = Field(None, max_length=500, description="原始来源URL")
    source_platform: Optional[str] = Field(None, max_length=50, description="来源平台（小红书/Instagram等）")


class InspirationImageCreate(InspirationImageBase):
    """创建灵感图请求"""
    image_path: str = Field(..., max_length=500, description="图片存储路径")


class InspirationImageUpdate(BaseModel):
    """更新灵感图请求（所有字段可选）"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = Field(None, max_length=500)
    source_platform: Optional[str] = Field(None, max_length=50)


class InspirationImageResponse(InspirationImageBase):
    """灵感图响应"""
    id: int
    user_id: int
    image_path: str
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InspirationImageListResponse(BaseModel):
    """灵感图列表响应"""
    total: int
    inspirations: List[InspirationImageResponse]
