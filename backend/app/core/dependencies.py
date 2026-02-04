"""
依赖注入函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User

# OAuth2 配置（JWT token 从 Authorization header 中提取）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    从 JWT token 中提取当前用户

    Args:
        token: JWT token
        db: 数据库会话

    Returns:
        User: 当前用户对象

    Raises:
        HTTPException: token 无效或用户不存在
    """
    # TODO: 实现 JWT token 验证逻辑
    # 1. 解析 JWT token
    # 2. 提取 user_id
    # 3. 从数据库查询用户
    # 4. 验证用户是否激活

    # 临时实现：返回第一个用户（仅用于开发测试）
    # 生产环境必须实现真正的 JWT 验证
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未找到用户，请先创建用户账号",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活用户

    Args:
        current_user: 当前用户

    Returns:
        User: 激活的用户对象

    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号未激活"
        )
    return current_user
