from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ==================== Design Plan Schemas ====================

class DesignPlanBase(BaseModel):
    """设计方案基础 Schema"""
    customer_id: Optional[int] = Field(None, description="客户ID（可选）")
    title: Optional[str] = Field(None, max_length=200, description="设计方案标题")
    notes: Optional[str] = Field(None, description="备注")


class DesignGenerateRequest(BaseModel):
    """AI生成设计请求"""
    customer_id: Optional[int] = Field(None, description="客户ID（可选）")
    prompt: str = Field(..., min_length=1, max_length=5000, description="设计描述提示词")
    reference_images: Optional[List[str]] = Field(None, description="参考图片路径列表")
    design_target: str = Field("10nails", description="设计目标（single/5nails/10nails）")
    style_keywords: Optional[List[str]] = Field(None, description="风格关键词列表")
    title: Optional[str] = Field(None, max_length=200, description="设计方案标题")
    notes: Optional[str] = Field(None, description="备注")


class DesignRefineRequest(BaseModel):
    """设计优化请求"""
    refinement_instruction: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="优化指令（如：增加更多亮片、让渐变更加自然等）"
    )


class DesignPlanUpdate(BaseModel):
    """更新设计方案请求（所有字段可选）"""
    title: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class DesignPlanResponse(DesignPlanBase):
    """设计方案响应"""
    id: int
    user_id: int

    # AI 生成信息
    ai_prompt: str
    generated_image_path: str
    model_version: Optional[str]

    # 设计参数
    design_target: Optional[str]
    style_keywords: Optional[List[str]]
    reference_images: Optional[List[str]]

    # 版本控制
    parent_design_id: Optional[int]
    version: int
    refinement_instruction: Optional[str]

    # AI 估算信息
    estimated_duration: Optional[int]
    estimated_materials: Optional[List[str]]
    difficulty_level: Optional[str]

    # 其他信息
    is_archived: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DesignPlanListResponse(BaseModel):
    """设计方案列表响应"""
    total: int
    designs: List[DesignPlanResponse]


class DesignEstimation(BaseModel):
    """设计执行估算"""
    estimated_duration: int = Field(..., description="预估耗时（分钟）")
    difficulty_level: str = Field(..., description="难度等级")
    materials: List[str] = Field(..., description="材料清单")
    techniques: List[str] = Field(..., description="技法清单")
