"""
设计方案 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.limiter import limiter
from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.design import (
    DesignGenerateRequest,
    DesignRefineRequest,
    DesignPlanUpdate,
    DesignPlanResponse,
    DesignPlanListResponse,
)
from app.services.design_service import DesignService

router = APIRouter()


@router.post(
    "/generate",
    response_model=DesignPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI生成设计方案",
    description="使用AI生成美甲设计方案（调用DALL-E 3）"
)
@limiter.limit("10/hour")
async def generate_design(
    request: Request,
    design_request: DesignGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    AI生成设计方案

    **请求体**:
    - **prompt**: 设计描述提示词（必填）
    - **reference_images**: 参考图片路径列表（可选）
    - **design_target**: 设计目标（single/5nails/10nails，默认10nails）
    - **style_keywords**: 风格关键词列表（可选）
    - **customer_id**: 客户ID（可选）
    - **title**: 设计方案标题（可选）
    - **notes**: 备注（可选）

    **返回**: 创建的设计方案（包含AI生成的图片URL和执行估算）

    **说明**:
    - 调用DALL-E 3生成设计图
    - 自动调用GPT-4 Vision估算执行难度、耗时和材料
    """
    return await DesignService.generate_design(db, design_request, current_user.id)


@router.post(
    "/{design_id}/refine",
    response_model=DesignPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="优化设计方案",
    description="基于现有设计生成优化版本（调用GPT-4 Vision + DALL-E 3）"
)
@limiter.limit("10/hour")
async def refine_design(
    request: Request,
    design_id: int,
    refine_request: DesignRefineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    优化设计方案（创建新版本）

    **路径参数**:
    - **design_id**: 原设计方案ID

    **请求体**:
    - **refinement_instruction**: 优化指令（如：增加更多亮片、让渐变更加自然等）

    **返回**: 新创建的优化版本设计方案

    **说明**:
    - 基于原设计图和优化指令生成新版本
    - 自动创建版本链接（parent_design_id）
    - 版本号自动递增
    """
    return await DesignService.refine_design(db, design_id, refine_request, current_user.id)


@router.get(
    "",
    response_model=DesignPlanListResponse,
    summary="获取设计方案列表",
    description="获取当前用户的设计方案列表，支持分页、过滤和搜索"
)
async def list_designs(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    customer_id: Optional[int] = Query(None, description="客户ID过滤"),
    is_archived: Optional[int] = Query(None, description="归档状态（0=未归档，1=已归档）"),
    search: Optional[str] = Query(None, description="搜索关键词（在标题、提示词中搜索）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取设计方案列表

    **查询参数**:
    - **skip**: 跳过记录数（分页偏移）
    - **limit**: 返回记录数（每页数量，最大1000）
    - **customer_id**: 客户ID过滤（可选）
    - **is_archived**: 归档状态（0=未归档，1=已归档，null=全部）
    - **search**: 搜索关键词（搜索标题或提示词）

    **返回**:
    - **total**: 符合条件的总记录数
    - **designs**: 设计方案列表
    """
    designs, total = DesignService.list_designs(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        is_archived=is_archived,
        search=search
    )

    return DesignPlanListResponse(total=total, designs=designs)


@router.get(
    "/recent",
    response_model=List[DesignPlanResponse],
    summary="获取最近设计方案",
    description="获取最近创建的设计方案"
)
async def get_recent_designs(
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取最近创建的设计方案

    **查询参数**:
    - **limit**: 返回记录数（默认10，最大100）

    **返回**: 设计方案列表（按创建时间倒序）
    """
    return DesignService.get_recent_designs(
        db,
        user_id=current_user.id,
        limit=limit
    )


@router.get(
    "/{design_id}",
    response_model=DesignPlanResponse,
    summary="获取设计方案详情",
    description="获取指定ID的设计方案详情"
)
async def get_design(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取设计方案详情

    **路径参数**:
    - **design_id**: 设计方案ID

    **返回**: 设计方案详情（包含AI生成信息和执行估算）
    """
    design = DesignService.get_design_by_id(
        db, design_id, current_user.id
    )

    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设计方案 ID {design_id} 不存在"
        )

    return design


@router.get(
    "/{design_id}/versions",
    response_model=List[DesignPlanResponse],
    summary="获取设计方案版本历史",
    description="获取设计方案的所有版本（用于查看迭代历史）"
)
async def get_design_versions(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取设计方案版本历史

    **路径参数**:
    - **design_id**: 设计方案ID

    **返回**: 版本历史列表（按版本号升序）

    **说明**:
    - 如果查询的是子版本，会返回整个版本链（从根版本开始）
    - 包含每个版本的优化指令（refinement_instruction）
    """
    versions = DesignService.get_design_versions(
        db, design_id, current_user.id
    )

    if not versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设计方案 ID {design_id} 不存在"
        )

    return versions


@router.put(
    "/{design_id}",
    response_model=DesignPlanResponse,
    summary="更新设计方案",
    description="更新设计方案的标题、备注等信息"
)
async def update_design(
    design_id: int,
    design: DesignPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新设计方案信息

    **路径参数**:
    - **design_id**: 设计方案ID

    **请求体**:
    - **title**: 设计方案标题（可选）
    - **notes**: 备注（可选）

    **说明**: 不能修改AI生成的信息（图片、提示词、估算等）
    """
    updated_design = DesignService.update_design(
        db, design_id, current_user.id, design
    )

    if not updated_design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设计方案 ID {design_id} 不存在"
        )

    return updated_design


@router.put(
    "/{design_id}/archive",
    response_model=DesignPlanResponse,
    summary="归档设计方案",
    description="归档设计方案（不删除，仅标记为已归档）"
)
async def archive_design(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    归档设计方案

    **路径参数**:
    - **design_id**: 设计方案ID

    **返回**: 归档后的设计方案

    **说明**: 归档后的设计方案不会在默认列表中显示，但仍可通过ID查询
    """
    archived_design = DesignService.archive_design(
        db, design_id, current_user.id
    )

    if not archived_design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设计方案 ID {design_id} 不存在"
        )

    return archived_design


@router.delete(
    "/{design_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除设计方案",
    description="删除指定ID的设计方案"
)
async def delete_design(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除设计方案

    **路径参数**:
    - **design_id**: 设计方案ID

    **返回**: 204 No Content（删除成功）

    **警告**: 删除操作不可恢复
    """
    success = DesignService.delete_design(
        db, design_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设计方案 ID {design_id} 不存在"
        )

    return None
