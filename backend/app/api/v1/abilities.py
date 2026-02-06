"""
能力维度 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.ability import (
    AbilityDimensionResponse,
    AbilityDimensionListResponse,
    AbilityStatsResponse,
    AbilityTrendResponse,
    AbilitySummaryResponse,
)
from app.services.ability_service import AbilityService

router = APIRouter()


@router.get(
    "/dimensions",
    response_model=AbilityDimensionListResponse,
    summary="获取所有能力维度",
    description="列出所有启用的能力维度（用于雷达图等）"
)
async def list_dimensions(
    include_inactive: bool = Query(False, description="是否包含未启用的维度"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有能力维度

    **查询参数**:
    - **include_inactive**: 是否包含未启用的维度（默认 False）

    **返回**:
    - **total**: 维度总数
    - **dimensions**: 维度列表（按 display_order 排序）

    **说明**:
    - 默认只返回启用的维度（is_active=1）
    - 6 个核心维度：颜色搭配、图案精度、细节处理、整体构图、技法运用、创意表达
    """
    dimensions = AbilityService.list_dimensions(db, include_inactive)

    return AbilityDimensionListResponse(
        total=len(dimensions),
        dimensions=dimensions
    )


@router.post(
    "/dimensions/init",
    status_code=status.HTTP_201_CREATED,
    summary="初始化能力维度",
    description="初始化预设的 6 个核心能力维度（幂等操作）"
)
async def initialize_dimensions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    初始化预设的 6 个核心能力维度

    **返回**:
    - **created_count**: 新创建的维度数量
    - **message**: 操作说明

    **说明**:
    - 这是一个幂等操作，如果维度已存在则跳过
    - 预设维度：颜色搭配、图案精度、细节处理、整体构图、技法运用、创意表达
    - 适用于首次系统初始化或数据修复
    """
    created_count = AbilityService.initialize_dimensions(db)

    return {
        "created_count": created_count,
        "message": f"能力维度初始化完成，新建 {created_count} 个维度"
    }


@router.get(
    "/stats",
    response_model=AbilityStatsResponse,
    summary="获取能力统计",
    description="获取当前用户的能力雷达图数据"
)
async def get_ability_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取能力统计（雷达图数据）

    **返回**:
    - **dimensions**: 维度名称列表
    - **scores**: 对应的平均分列表
    - **avg_score**: 所有维度的总平均分
    - **total_records**: 总能力评分记录数

    **说明**:
    - 每个维度的分数是该维度所有服务记录评分的平均值
    - 分数范围 0-100
    - 如果某个维度没有评分记录，则显示为 0
    """
    stats = AbilityService.get_ability_stats(db, current_user.id)

    return AbilityStatsResponse(**stats)


@router.get(
    "/summary",
    response_model=AbilitySummaryResponse,
    summary="获取能力总结",
    description="获取擅长和待提升的能力维度总结"
)
async def get_ability_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取能力总结（擅长/待提升）

    **返回**:
    - **strengths**: 擅长的维度（评分前 3 名）
    - **improvements**: 待提升的维度（评分后 3 名）
    - **total_services**: 总服务次数

    **说明**:
    - 根据各维度的平均分排序
    - 用于能力中心的总结展示
    """
    summary = AbilityService.get_ability_summary(db, current_user.id)

    return AbilitySummaryResponse(**summary)


@router.get(
    "/trend/{dimension_name}",
    response_model=AbilityTrendResponse,
    summary="获取能力成长趋势",
    description="获取指定维度的历史评分趋势（用于趋势图）"
)
async def get_ability_trend(
    dimension_name: str,
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取能力成长趋势

    **路径参数**:
    - **dimension_name**: 维度名称（如：颜色搭配）

    **查询参数**:
    - **limit**: 返回的最大记录数（默认 20，最大 100）

    **返回**:
    - **dimension_name**: 维度名称
    - **data_points**: 数据点列表（包含 date、score、service_record_id）

    **说明**:
    - 按时间升序返回历史评分记录
    - 用于绘制能力成长趋势图
    """
    trend = AbilityService.get_ability_trend(
        db, current_user.id, dimension_name, limit
    )

    if not trend["data_points"]:
        # 如果维度不存在或没有记录，返回 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到维度 '{dimension_name}' 的评分记录"
        )

    return AbilityTrendResponse(**trend)
