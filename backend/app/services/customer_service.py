"""
客户管理业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from fastapi import HTTPException, status

from app.models.customer import Customer
from app.models.customer_profile import CustomerProfile
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerProfileCreate,
    CustomerProfileUpdate,
)


class CustomerService:
    """客户管理服务"""

    @staticmethod
    def create_customer(
        db: Session,
        customer_data: CustomerCreate,
        user_id: int
    ) -> Customer:
        """
        创建客户

        Args:
            db: 数据库会话
            customer_data: 客户创建数据
            user_id: 所属美甲师ID

        Returns:
            Customer: 创建的客户对象

        Raises:
            HTTPException: 手机号已存在时抛出409错误
        """
        # 检查手机号是否已存在
        existing = db.query(Customer).filter(
            Customer.phone == customer_data.phone
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"手机号 {customer_data.phone} 已被使用"
            )

        # 创建客户
        customer = Customer(
            **customer_data.model_dump(),
            user_id=user_id
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

    @staticmethod
    def get_customer_by_id(
        db: Session,
        customer_id: int,
        user_id: int
    ) -> Optional[Customer]:
        """
        根据ID获取客户（包含档案）

        Args:
            db: 数据库会话
            customer_id: 客户ID
            user_id: 所属美甲师ID

        Returns:
            Optional[Customer]: 客户对象（不存在时返回None）
        """
        return db.query(Customer).filter(
            and_(
                Customer.id == customer_id,
                Customer.user_id == user_id
            )
        ).first()

    @staticmethod
    def list_customers(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Customer], int]:
        """
        获取客户列表（分页 + 搜索）

        Args:
            db: 数据库会话
            user_id: 所属美甲师ID
            skip: 跳过记录数
            limit: 返回记录数
            search: 搜索关键词（搜索姓名、手机号）
            is_active: 是否活跃（None表示不过滤）

        Returns:
            tuple[List[Customer], int]: (客户列表, 总数)
        """
        query = db.query(Customer).filter(Customer.user_id == user_id)

        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.name.like(search_pattern),
                    Customer.phone.like(search_pattern)
                )
            )

        # 活跃状态过滤
        if is_active is not None:
            query = query.filter(Customer.is_active == (1 if is_active else 0))

        # 获取总数
        total = query.count()

        # 分页
        customers = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()

        return customers, total

    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        user_id: int,
        update_data: CustomerUpdate
    ) -> Optional[Customer]:
        """
        更新客户信息

        Args:
            db: 数据库会话
            customer_id: 客户ID
            user_id: 所属美甲师ID
            update_data: 更新数据

        Returns:
            Optional[Customer]: 更新后的客户（不存在时返回None）

        Raises:
            HTTPException: 手机号冲突时抛出409错误
        """
        customer = CustomerService.get_customer_by_id(db, customer_id, user_id)

        if not customer:
            return None

        # 如果更新手机号，检查是否冲突
        if update_data.phone and update_data.phone != customer.phone:
            existing = db.query(Customer).filter(
                and_(
                    Customer.phone == update_data.phone,
                    Customer.id != customer_id
                )
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"手机号 {update_data.phone} 已被使用"
                )

        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)

        return customer

    @staticmethod
    def delete_customer(
        db: Session,
        customer_id: int,
        user_id: int
    ) -> bool:
        """
        删除客户（软删除：设置 is_active = 0）

        Args:
            db: 数据库会话
            customer_id: 客户ID
            user_id: 所属美甲师ID

        Returns:
            bool: 是否成功删除
        """
        customer = CustomerService.get_customer_by_id(db, customer_id, user_id)

        if not customer:
            return False

        # 软删除
        customer.is_active = 0
        db.commit()

        return True

    @staticmethod
    def create_or_update_profile(
        db: Session,
        customer_id: int,
        user_id: int,
        profile_data: CustomerProfileCreate | CustomerProfileUpdate
    ) -> Optional[CustomerProfile]:
        """
        创建或更新客户档案

        Args:
            db: 数据库会话
            customer_id: 客户ID
            user_id: 所属美甲师ID
            profile_data: 档案数据

        Returns:
            Optional[CustomerProfile]: 档案对象（客户不存在时返回None）
        """
        # 验证客户存在且属于当前用户
        customer = CustomerService.get_customer_by_id(db, customer_id, user_id)

        if not customer:
            return None

        # 查找现有档案
        existing_profile = db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == customer_id
        ).first()

        if existing_profile:
            # 更新现有档案
            update_dict = profile_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if field != "customer_id":  # 不更新 customer_id
                    setattr(existing_profile, field, value)

            db.commit()
            db.refresh(existing_profile)
            return existing_profile
        else:
            # 创建新档案
            profile = CustomerProfile(
                customer_id=customer_id,
                **profile_data.model_dump(exclude={"customer_id"})
            )

            db.add(profile)
            db.commit()
            db.refresh(profile)

            return profile

    @staticmethod
    def get_profile(
        db: Session,
        customer_id: int,
        user_id: int
    ) -> Optional[CustomerProfile]:
        """
        获取客户档案

        Args:
            db: 数据库会话
            customer_id: 客户ID
            user_id: 所属美甲师ID

        Returns:
            Optional[CustomerProfile]: 档案对象
        """
        # 验证客户存在且属于当前用户
        customer = CustomerService.get_customer_by_id(db, customer_id, user_id)

        if not customer:
            return None

        return db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == customer_id
        ).first()
