"""
能力维度相关的 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AbilityDimensionBase(BaseModel):
    """能力维度基础 Schema"""
    name: str = Field(..., description="维度名称（中文）")
    name_en: Optional[str] = Field(None, description="维度英文名称")
    description: Optional[str] = Field(None, description="维度描述")
    scoring_criteria: Optional[str] = Field(None, description="评分标准说明")
    display_order: int = Field(0, description="显示顺序")
    is_active: int = Field(1, description="是否启用（1=是，0=否）")


class AbilityDimensionCreate(AbilityDimensionBase):
    """创建能力维度 Schema"""
    pass


class AbilityDimensionUpdate(BaseModel):
    """更新能力维度 Schema"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    scoring_criteria: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[int] = None


class AbilityDimensionResponse(AbilityDimensionBase):
    """能力维度响应 Schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AbilityDimensionListResponse(BaseModel):
    """能力维度列表响应"""
    total: int
    dimensions: List[AbilityDimensionResponse]


class AbilityRecordBase(BaseModel):
    """能力记录基础 Schema"""
    dimension_id: int = Field(..., description="维度ID")
    score: int = Field(..., ge=0, le=100, description="评分（0-100）")
    evidence: Optional[str] = Field(None, description="评分依据")


class AbilityRecordCreate(AbilityRecordBase):
    """创建能力记录 Schema"""
    user_id: int
    service_record_id: int


class AbilityRecordResponse(AbilityRecordBase):
    """能力记录响应 Schema"""
    id: int
    user_id: int
    service_record_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AbilityStatsResponse(BaseModel):
    """能力统计响应（雷达图数据）"""
    dimensions: List[str] = Field(..., description="维度名称列表")
    scores: List[int] = Field(..., description="对应的评分列表")
    avg_score: float = Field(..., description="平均分")
    total_records: int = Field(..., description="总记录数")


class AbilityTrendPoint(BaseModel):
    """能力趋势数据点"""
    date: datetime
    score: int
    service_record_id: int


class AbilityTrendResponse(BaseModel):
    """能力趋势响应"""
    dimension_name: str
    data_points: List[AbilityTrendPoint]


class AbilitySummaryResponse(BaseModel):
    """能力总结响应（擅长/待提升）"""
    strengths: List[dict] = Field(..., description="擅长的维度（前3名）")
    improvements: List[dict] = Field(..., description="待提升的维度（后3名）")
    total_services: int = Field(..., description="总服务次数")
