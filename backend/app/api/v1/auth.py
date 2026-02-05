"""
认证 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户账号"
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **email**: 用户邮箱（必须唯一）
    - **username**: 用户名（必须唯一，3-50字符）
    - **password**: 密码（至少6位）

    **返回**: 创建的用户信息（不包含密码）
    """
    user = AuthService.register_user(db, user_data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用邮箱/用户名和密码登录，返回JWT token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录

    **表单字段**:
    - **username**: 邮箱或用户名
    - **password**: 密码

    **返回**: JWT Access Token 和 Refresh Token
    """
    # 验证用户凭据
    user = AuthService.authenticate_user(
        db,
        email_or_username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱/用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号未激活"
        )

    # 创建 Access Token 和 Refresh Token
    tokens = AuthService.create_tokens(user.id)

    return tokens


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新 Access Token",
    description="使用 Refresh Token 获取新的 Access Token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新 Access Token

    **请求体**:
    - **refresh_token**: Refresh Token

    **返回**: 新的 Access Token
    """
    tokens = AuthService.refresh_access_token(db, request.refresh_token)
    return tokens


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="用户登出",
    description="登出用户（客户端需清除 token）"
)
async def logout():
    """
    用户登出

    **说明**:
    - JWT 是无状态的，服务端不存储 token
    - 登出需要客户端删除本地存储的 token
    - 如需服务端控制 token 失效，需要实现 token 黑名单（使用 Redis）

    **返回**: 204 No Content
    """
    # JWT 是无状态的，实际的登出逻辑在客户端
    # 客户端应该删除存储的 access_token 和 refresh_token
    return None
