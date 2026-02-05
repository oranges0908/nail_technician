"""
安全工具：密码哈希、JWT Token生成与验证
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密上下文（使用 bcrypt）
# truncate_error=True 防止 bcrypt 72字节限制问题
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码哈希
    """
    # bcrypt限制密码最长72字节，超过部分会被截断
    # 这里主动截断以避免警告
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确

    Args:
        plain_password: 明文密码
        hashed_password: 数据库中的密码哈希

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: int | str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    创建 Access Token (JWT)

    Args:
        subject: Token 主体（通常是 user_id）
        expires_delta: 过期时间增量（默认使用配置值）
        additional_claims: 额外的 JWT claims

    Returns:
        str: JWT Access Token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access"
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(
    subject: int | str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 Refresh Token (JWT)

    Args:
        subject: Token 主体（通常是 user_id）
        expires_delta: 过期时间增量（默认使用配置值）

    Returns:
        str: JWT Refresh Token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    解码 JWT Token

    Args:
        token: JWT token 字符串

    Returns:
        Dict[str, Any]: Token payload

    Raises:
        JWTError: Token 无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token 验证失败: {str(e)}")


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    验证 Token 类型

    Args:
        payload: Token payload
        expected_type: 期望的 token 类型（"access" 或 "refresh"）

    Returns:
        bool: 类型是否匹配
    """
    return payload.get("type") == expected_type
