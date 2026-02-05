"""
用户管理服务层

提供用户CRUD操作的业务逻辑。
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError,
    AuthenticationError
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class UserService:
    """用户管理服务"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        根据ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            User: 用户对象

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"用户不存在: user_id={user_id}")
            raise ResourceNotFoundError(resource="用户", resource_id=user_id)

        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            db: 数据库会话
            email: 用户邮箱

        Returns:
            Optional[User]: 用户对象或None
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
            Optional[User]: 用户对象或None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        is_superuser: bool = False
    ) -> User:
        """
        创建新用户

        Args:
            db: 数据库会话
            email: 用户邮箱
            username: 用户名
            password: 明文密码
            is_superuser: 是否为超级管理员

        Returns:
            User: 创建的用户对象

        Raises:
            ResourceConflictError: 邮箱或用户名已被使用
        """
        # 检查邮箱是否已存在
        existing_user = UserService.get_user_by_email(db, email)
        if existing_user:
            logger.warning(f"邮箱已被使用: {email}")
            raise ResourceConflictError(
                message=f"邮箱 {email} 已被使用",
                detail={"email": email}
            )

        # 检查用户名是否已存在
        existing_user = UserService.get_user_by_username(db, username)
        if existing_user:
            logger.warning(f"用户名已被使用: {username}")
            raise ResourceConflictError(
                message=f"用户名 {username} 已被使用",
                detail={"username": username}
            )

        # 创建用户
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_superuser=is_superuser
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"用户创建成功: user_id={user.id}, username={username}")
            return user
        except IntegrityError as e:
            db.rollback()
            logger.error(f"用户创建失败: {e}")
            raise ResourceConflictError(
                message="用户创建失败：邮箱或用户名已被使用",
                detail={"error": str(e)}
            )

    @staticmethod
    def update_user(
        db: Session,
        user: User,
        update_data: Dict[str, Any],
        check_conflicts: bool = True
    ) -> User:
        """
        更新用户信息

        Args:
            db: 数据库会话
            user: 要更新的用户对象
            update_data: 更新数据字典
            check_conflicts: 是否检查邮箱/用户名冲突

        Returns:
            User: 更新后的用户对象

        Raises:
            ResourceConflictError: 邮箱或用户名已被使用
        """
        # 检查邮箱冲突
        if check_conflicts and "email" in update_data:
            new_email = update_data["email"]
            if new_email != user.email:
                existing_user = db.query(User).filter(
                    User.email == new_email,
                    User.id != user.id
                ).first()

                if existing_user:
                    logger.warning(f"邮箱已被使用: {new_email}")
                    raise ResourceConflictError(
                        message=f"邮箱 {new_email} 已被使用",
                        detail={"email": new_email}
                    )

        # 检查用户名冲突
        if check_conflicts and "username" in update_data:
            new_username = update_data["username"]
            if new_username != user.username:
                existing_user = db.query(User).filter(
                    User.username == new_username,
                    User.id != user.id
                ).first()

                if existing_user:
                    logger.warning(f"用户名已被使用: {new_username}")
                    raise ResourceConflictError(
                        message=f"用户名 {new_username} 已被使用",
                        detail={"username": new_username}
                    )

        # 如果更新密码，需要加密
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        # 更新字段
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        db.commit()
        db.refresh(user)

        logger.info(f"用户更新成功: user_id={user.id}")
        return user

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        old_password: str,
        new_password: str
    ) -> User:
        """
        修改用户密码

        Args:
            db: 数据库会话
            user: 用户对象
            old_password: 旧密码（明文）
            new_password: 新密码（明文）

        Returns:
            User: 更新后的用户对象

        Raises:
            AuthenticationError: 旧密码错误
            ValidationError: 新密码不符合要求
        """
        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"密码修改失败：旧密码错误 - user_id={user.id}")
            raise AuthenticationError(
                message="旧密码错误",
                detail={"user_id": user.id}
            )

        # 验证新密码长度
        if len(new_password) < 6:
            raise ValidationError(
                message="新密码长度不足",
                detail={"min_length": 6, "actual_length": len(new_password)}
            )

        # 更新密码
        user.hashed_password = hash_password(new_password)

        db.commit()
        db.refresh(user)

        logger.info(f"密码修改成功: user_id={user.id}")
        return user

    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        """
        停用用户（软删除）

        Args:
            db: 数据库会话
            user: 用户对象

        Returns:
            User: 停用后的用户对象
        """
        user.is_active = False

        db.commit()
        db.refresh(user)

        logger.info(f"用户已停用: user_id={user.id}, username={user.username}")
        return user

    @staticmethod
    def activate_user(db: Session, user: User) -> User:
        """
        激活用户

        Args:
            db: 数据库会话
            user: 用户对象

        Returns:
            User: 激活后的用户对象
        """
        user.is_active = True

        db.commit()
        db.refresh(user)

        logger.info(f"用户已激活: user_id={user.id}, username={user.username}")
        return user

    @staticmethod
    def get_active_users_count(db: Session) -> int:
        """
        获取激活用户数量

        Args:
            db: 数据库会话

        Returns:
            int: 激活用户数量
        """
        return db.query(User).filter(User.is_active == True).count()

    @staticmethod
    def get_total_users_count(db: Session) -> int:
        """
        获取总用户数量

        Args:
            db: 数据库会话

        Returns:
            int: 总用户数量
        """
        return db.query(User).count()
