"""
认证服务 - 用户注册、登录、Token刷新
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from jose import JWTError


class AuthService:
    """认证服务类"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        注册新用户

        Args:
            db: 数据库会话
            user_data: 用户创建数据

        Returns:
            User: 创建的用户对象

        Raises:
            HTTPException: 用户名或邮箱已存在
        """
        # 检查用户名或邮箱是否已存在
        existing_user = db.query(User).filter(
            or_(
                User.email == user_data.email,
                User.username == user_data.username
            )
        ).first()

        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"邮箱 {user_data.email} 已被注册"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"用户名 {user_data.username} 已被使用"
                )

        # 创建新用户（密码加密）
        hashed_password = hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def authenticate_user(
        db: Session,
        email_or_username: str,
        password: str
    ) -> Optional[User]:
        """
        验证用户凭据

        Args:
            db: 数据库会话
            email_or_username: 邮箱或用户名
            password: 密码

        Returns:
            Optional[User]: 认证成功返回用户对象，失败返回 None
        """
        # 查找用户（支持邮箱或用户名登录）
        user = db.query(User).filter(
            or_(
                User.email == email_or_username,
                User.username == email_or_username
            )
        ).first()

        if not user:
            return None

        # 验证密码
        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_tokens(user_id: int) -> dict:
        """
        创建 Access Token 和 Refresh Token

        Args:
            user_id: 用户ID

        Returns:
            dict: 包含 access_token 和 refresh_token
        """
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """
        使用 Refresh Token 刷新 Access Token

        Args:
            db: 数据库会话
            refresh_token: Refresh Token

        Returns:
            dict: 新的 access_token

        Raises:
            HTTPException: Refresh Token 无效或过期
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Refresh Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # 解码 Refresh Token
            payload = decode_token(refresh_token)

            # 验证 token 类型（必须是 refresh token）
            if not verify_token_type(payload, "refresh"):
                raise credentials_exception

            # 提取 user_id
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        # 验证用户是否存在且激活
        user = db.query(User).filter(User.id == int(user_id)).first()

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账号未激活"
            )

        # 创建新的 Access Token
        new_access_token = create_access_token(subject=user.id)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            db: 数据库会话
            email: 用户邮箱

        Returns:
            Optional[User]: 用户对象或 None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            Optional[User]: 用户对象或 None
        """
        return db.query(User).filter(User.username == username).first()
