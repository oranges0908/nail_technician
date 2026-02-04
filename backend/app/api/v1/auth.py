from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录
    """
    # TODO: 实现登录逻辑
    # 1. 验证用户凭据
    # 2. 生成 JWT token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login endpoint not implemented yet"
    )


@router.post("/register", response_model=Token)
async def register(
    db: Session = Depends(get_db)
):
    """
    用户注册
    """
    # TODO: 实现注册逻辑
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Register endpoint not implemented yet"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token():
    """
    刷新访问令牌
    """
    # TODO: 实现令牌刷新逻辑
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token endpoint not implemented yet"
    )
