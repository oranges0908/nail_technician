"""
用户管理 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserPasswordUpdate
from app.core.security import hash_password, verify_password

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息

    **需要认证**: 是

    **返回**: 当前用户的详细信息
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="更新当前用户信息",
    description="更新当前登录用户的信息（邮箱、用户名等）"
)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新当前用户信息

    **需要认证**: 是

    **请求体** (所有字段可选):
    - **email**: 新邮箱
    - **username**: 新用户名
    - **password**: 新密码（会自动加密）

    **返回**: 更新后的用户信息
    """
    # 检查邮箱是否被其他用户使用
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"邮箱 {user_update.email} 已被使用"
            )

    # 检查用户名是否被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"用户名 {user_update.username} 已被使用"
            )

    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)

    # 如果更新密码，需要加密
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.put(
    "/me/password",
    response_model=UserResponse,
    summary="修改密码",
    description="修改当前用户的密码（需要提供旧密码）"
)
async def change_password(
    password_update: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    修改密码

    **需要认证**: 是

    **请求体**:
    - **old_password**: 旧密码（用于验证）
    - **new_password**: 新密码（至少6位）

    **返回**: 更新后的用户信息
    """
    # 验证旧密码
    if not verify_password(password_update.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    current_user.hashed_password = hash_password(password_update.new_password)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="获取指定用户信息",
    description="获取指定用户的详细信息（需要超级管理员权限）"
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    获取指定用户信息

    **需要认证**: 是（超级管理员）

    **路径参数**:
    - **user_id**: 用户ID

    **返回**: 用户详细信息
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户不存在 (ID: {user_id})"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="更新指定用户信息",
    description="更新指定用户的信息（需要超级管理员权限）"
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    更新指定用户信息

    **需要认证**: 是（超级管理员）

    **路径参数**:
    - **user_id**: 用户ID

    **请求体** (所有字段可选):
    - **email**: 新邮箱
    - **username**: 新用户名
    - **password**: 新密码
    - **is_active**: 是否激活

    **返回**: 更新后的用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户不存在 (ID: {user_id})"
        )

    # 检查邮箱冲突
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"邮箱 {user_update.email} 已被使用"
            )

    # 检查用户名冲突
    if user_update.username and user_update.username != user.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != user_id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"用户名 {user_update.username} 已被使用"
            )

    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)

    # 如果更新密码，需要加密
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除当前用户账号",
    description="删除当前登录用户的账号（软删除，设置 is_active=false）"
)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除当前用户账号（软删除）

    **需要认证**: 是

    **说明**:
    - 执行软删除，将 `is_active` 设置为 `false`
    - 用户数据不会真正删除，仅标记为不活跃
    - 删除后无法再登录，但历史数据保留

    **返回**: 204 No Content
    """
    # 软删除当前用户
    current_user.is_active = False

    db.commit()

    return None


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除指定用户",
    description="删除指定用户（软删除，设置 is_active=false，需要超级管理员权限）"
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    删除用户（软删除）

    **需要认证**: 是（超级管理员）

    **路径参数**:
    - **user_id**: 用户ID

    **说明**: 执行软删除，将 `is_active` 设置为 `false`

    **返回**: 204 No Content
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户不存在 (ID: {user_id})"
        )

    # 不允许删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号，请使用 DELETE /me"
        )

    # 软删除
    user.is_active = False

    db.commit()

    return None
