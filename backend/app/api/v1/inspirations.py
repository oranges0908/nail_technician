"""
灵感图库 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.inspiration import (
    InspirationImageCreate,
    InspirationImageUpdate,
    InspirationImageResponse,
    InspirationImageListResponse,
)
from app.services.inspiration_service import InspirationService

router = APIRouter()


@router.post(
    "",
    response_model=InspirationImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建灵感图",
    description="上传并保存新的灵感图"
)
async def create_inspiration(
    inspiration: InspirationImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新的灵感图

    - **image_path**: 图片存储路径（必填）
    - **title**: 图片标题（可选）
    - **description**: 图片描述（可选）
    - **tags**: 标签列表（可选）
    - **category**: 分类（可选，如：法式/渐变/贴片/彩绘等）
    - **source_url**: 原始来源URL（可选）
    - **source_platform**: 来源平台（可选，如：小红书/Instagram等）
    """
    return InspirationService.create_inspiration(db, inspiration, current_user.id)


@router.get(
    "",
    response_model=InspirationImageListResponse,
    summary="获取灵感图列表",
    description="获取当前用户的灵感图列表，支持分页、过滤和搜索"
)
async def list_inspirations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    category: Optional[str] = Query(None, description="分类过滤（法式/渐变/贴片等）"),
    tags: Optional[List[str]] = Query(None, description="标签过滤（包含任一标签即返回）"),
    search: Optional[str] = Query(None, description="搜索关键词（在标题、描述中搜索）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取灵感图列表

    **查询参数**:
    - **skip**: 跳过记录数（分页偏移）
    - **limit**: 返回记录数（每页数量，最大1000）
    - **category**: 分类过滤
    - **tags**: 标签过滤（可多选）
    - **search**: 搜索关键词（搜索标题或描述）

    **返回**:
    - **total**: 符合条件的总记录数
    - **inspirations**: 灵感图列表
    """
    inspirations, total = InspirationService.list_inspirations(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        category=category,
        tags=tags,
        search=search
    )

    return InspirationImageListResponse(total=total, inspirations=inspirations)


@router.get(
    "/popular",
    response_model=List[InspirationImageResponse],
    summary="获取热门灵感图",
    description="获取使用次数最多的灵感图"
)
async def get_popular_inspirations(
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取热门灵感图（按使用次数排序）

    **查询参数**:
    - **limit**: 返回记录数（默认10，最大100）

    **返回**: 灵感图列表
    """
    return InspirationService.get_popular_inspirations(
        db,
        user_id=current_user.id,
        limit=limit
    )


@router.get(
    "/recent",
    response_model=List[InspirationImageResponse],
    summary="获取最近灵感图",
    description="获取最近添加的灵感图"
)
async def get_recent_inspirations(
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取最近添加的灵感图

    **查询参数**:
    - **limit**: 返回记录数（默认10，最大100）

    **返回**: 灵感图列表
    """
    return InspirationService.get_recent_inspirations(
        db,
        user_id=current_user.id,
        limit=limit
    )


@router.get(
    "/{inspiration_id}",
    response_model=InspirationImageResponse,
    summary="获取灵感图详情",
    description="获取指定ID的灵感图详情"
)
async def get_inspiration(
    inspiration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取灵感图详情

    **路径参数**:
    - **inspiration_id**: 灵感图ID

    **返回**: 灵感图详情
    """
    inspiration = InspirationService.get_inspiration_by_id(
        db, inspiration_id, current_user.id
    )

    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"灵感图 ID {inspiration_id} 不存在"
        )

    return inspiration


@router.put(
    "/{inspiration_id}",
    response_model=InspirationImageResponse,
    summary="更新灵感图",
    description="更新灵感图的标签、分类等信息"
)
async def update_inspiration(
    inspiration_id: int,
    inspiration: InspirationImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新灵感图信息

    **路径参数**:
    - **inspiration_id**: 灵感图ID

    **请求体**:
    - **title**: 图片标题（可选）
    - **description**: 图片描述（可选）
    - **tags**: 标签列表（可选）
    - **category**: 分类（可选）
    - **source_url**: 原始来源URL（可选）
    - **source_platform**: 来源平台（可选）
    """
    updated_inspiration = InspirationService.update_inspiration(
        db, inspiration_id, current_user.id, inspiration
    )

    if not updated_inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"灵感图 ID {inspiration_id} 不存在"
        )

    return updated_inspiration


@router.delete(
    "/{inspiration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除灵感图",
    description="删除指定ID的灵感图"
)
async def delete_inspiration(
    inspiration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除灵感图

    **路径参数**:
    - **inspiration_id**: 灵感图ID

    **返回**: 204 No Content（删除成功）
    """
    success = InspirationService.delete_inspiration(
        db, inspiration_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"灵感图 ID {inspiration_id} 不存在"
        )

    return None


@router.post(
    "/{inspiration_id}/use",
    response_model=InspirationImageResponse,
    summary="标记灵感图使用",
    description="增加灵感图的使用次数"
)
async def use_inspiration(
    inspiration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    标记灵感图被使用（增加使用次数）

    当美甲师在设计方案中使用某个灵感图时调用此接口

    **路径参数**:
    - **inspiration_id**: 灵感图ID

    **返回**: 更新后的灵感图详情
    """
    inspiration = InspirationService.increment_usage_count(
        db, inspiration_id, current_user.id
    )

    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"灵感图 ID {inspiration_id} 不存在"
        )

    return inspiration
