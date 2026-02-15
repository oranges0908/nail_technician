from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional


class ServiceRecordBase(BaseModel):
    """服务记录基础 Schema"""
    customer_id: int
    design_plan_id: Optional[int] = None
    service_date: date
    service_duration: Optional[int] = Field(None, description="服务时长（分钟）")

    # 新增字段
    materials_used: Optional[str] = Field(None, max_length=2000, description="实际使用的材料清单")
    artist_review: Optional[str] = Field(None, max_length=5000, description="美甲师复盘内容")
    customer_feedback: Optional[str] = Field(None, max_length=2000, description="客户反馈")
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="客户满意度评分（1-5星）")

    notes: Optional[str] = None

    @field_validator('customer_satisfaction')
    @classmethod
    def validate_satisfaction(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('客户满意度评分必须在 1-5 之间')
        return v


class ServiceRecordCreate(ServiceRecordBase):
    """创建服务记录"""
    pass


class ServiceRecordUpdate(BaseModel):
    """更新服务记录（所有字段可选）"""
    service_date: Optional[date] = None
    service_duration: Optional[int] = None
    actual_image_path: Optional[str] = None
    materials_used: Optional[str] = Field(None, max_length=2000)
    artist_review: Optional[str] = Field(None, max_length=5000)
    customer_feedback: Optional[str] = Field(None, max_length=2000)
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    status: Optional[str] = None

    @field_validator('customer_satisfaction')
    @classmethod
    def validate_satisfaction(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('客户满意度评分必须在 1-5 之间')
        return v


class ServiceRecordComplete(BaseModel):
    """完成服务记录（上传实际图并填写复盘）"""
    actual_image_path: str = Field(..., description="实际完成图路径")
    service_duration: int = Field(..., description="实际服务时长（分钟）")
    materials_used: Optional[str] = Field(None, max_length=2000)
    artist_review: Optional[str] = Field(None, max_length=5000)
    customer_feedback: Optional[str] = Field(None, max_length=2000)
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None

    @field_validator('customer_satisfaction')
    @classmethod
    def validate_satisfaction(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('客户满意度评分必须在 1-5 之间')
        return v


class ServiceRecordResponse(ServiceRecordBase):
    """服务记录响应"""
    id: int
    user_id: int
    actual_image_path: Optional[str] = None
    design_image_path: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComparisonResultResponse(BaseModel):
    """对比结果响应"""
    id: int
    service_record_id: int
    similarity_score: int
    differences: dict
    suggestions: list
    contextual_insights: Optional[dict] = None
    analyzed_at: datetime

    model_config = {"from_attributes": True}
