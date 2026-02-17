"""
客户管理 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerWithProfile,
    CustomerListResponse,
    CustomerProfileCreate,
    CustomerProfileUpdate,
    CustomerProfileResponse,
)
from app.services.customer_service import CustomerService

router = APIRouter()


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建客户",
    description="创建新客户，手机号必须唯一"
)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新客户

    - **name**: 客户姓名（必填）
    - **phone**: 联系电话（必填，唯一）
    - **email**: 电子邮件（可选）
    - **avatar_path**: 头像路径（可选）
    - **notes**: 备注（可选）
    - **is_active**: 是否活跃（默认 true）
    """
    return CustomerService.create_customer(db, customer, current_user.id)


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="获取客户列表",
    description="获取当前用户的客户列表，支持分页和搜索"
)
async def list_customers(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    search: Optional[str] = Query(None, description="搜索关键词（姓名/手机号）"),
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取客户列表

    **查询参数**:
    - **skip**: 跳过记录数（分页偏移）
    - **limit**: 返回记录数（每页数量，最大1000）
    - **search**: 搜索关键词（搜索姓名或手机号）
    - **is_active**: 是否活跃（true=活跃，false=已归档，null=全部）

    **返回**:
    - **total**: 符合条件的总记录数
    - **customers**: 客户列表
    """
    customers, total = CustomerService.list_customers(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )

    return CustomerListResponse(total=total, customers=customers)


@router.get(
    "/{customer_id}",
    response_model=CustomerWithProfile,
    summary="获取客户详情",
    description="获取客户详情（包含详细档案）"
)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取客户详情（包含档案）

    **路径参数**:
    - **customer_id**: 客户ID

    **返回**: 客户基本信息 + 详细档案（如果存在）
    """
    customer = CustomerService.get_customer_by_id(db, customer_id, current_user.id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"客户不存在 (ID: {customer_id})"
        )

    return customer


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="更新客户信息",
    description="更新客户基本信息"
)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新客户信息

    **路径参数**:
    - **customer_id**: 客户ID

    **请求体**: 所有字段可选，只更新提供的字段

    **注意**: 手机号必须唯一，冲突时返回 409 错误
    """
    updated_customer = CustomerService.update_customer(
        db,
        customer_id,
        current_user.id,
        customer_update
    )

    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"客户不存在 (ID: {customer_id})"
        )

    return updated_customer


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除客户",
    description="删除客户（软删除，设置 is_active = false）"
)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除客户（软删除）

    **路径参数**:
    - **customer_id**: 客户ID

    **说明**: 执行软删除，将 `is_active` 设置为 `false`，数据仍保留在数据库中
    """
    success = CustomerService.delete_customer(db, customer_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"客户不存在 (ID: {customer_id})"
        )

    return None


# ==================== Customer Profile Endpoints ====================

@router.put(
    "/{customer_id}/profile",
    response_model=CustomerProfileResponse,
    summary="创建或更新客户档案",
    description="创建或更新客户的详细档案（指甲特征、偏好等）"
)
async def create_or_update_profile(
    customer_id: int,
    profile_data: CustomerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建或更新客户档案

    **路径参数**:
    - **customer_id**: 客户ID

    **请求体**: 客户详细档案
    - **指甲特征**: nail_shape, nail_length, nail_condition, nail_photos
    - **颜色偏好**: color_preferences, color_dislikes
    - **风格偏好**: style_preferences, pattern_preferences
    - **禁忌**: allergies, prohibitions
    - **其他偏好**: occasion_preferences, maintenance_preference

    **行为**:
    - 如果档案不存在，创建新档案
    - 如果档案已存在，更新提供的字段
    """
    profile = CustomerService.create_or_update_profile(
        db,
        customer_id,
        current_user.id,
        profile_data
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"客户不存在 (ID: {customer_id})"
        )

    return profile


@router.get(
    "/{customer_id}/profile",
    response_model=CustomerProfileResponse,
    summary="获取客户档案",
    description="获取客户的详细档案"
)
async def get_profile(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取客户档案

    **路径参数**:
    - **customer_id**: 客户ID

    **返回**: 客户详细档案
    """
    profile = CustomerService.get_profile(db, customer_id, current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"客户或档案不存在 (Customer ID: {customer_id})"
        )

    return profile
