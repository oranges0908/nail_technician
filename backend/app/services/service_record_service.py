import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.service_record import ServiceRecord
from app.models.customer import Customer
from app.models.design_plan import DesignPlan

logger = logging.getLogger(__name__)


class ServiceRecordService:
    """服务记录业务逻辑服务"""

    @staticmethod
    def create_service(
        db: Session,
        service_data: Dict[str, Any],
        user_id: int
    ) -> ServiceRecord:
        """
        创建服务记录

        Args:
            db: 数据库会话
            service_data: 服务记录数据
            user_id: 用户ID

        Returns:
            ServiceRecord: 创建的服务记录

        Raises:
            ValueError: 客户不存在或不属于该用户
        """

        # 验证客户是否存在且属于该用户
        customer = db.query(Customer).filter(
            and_(
                Customer.id == service_data["customer_id"],
                Customer.user_id == user_id
            )
        ).first()

        if not customer:
            raise ValueError(f"客户 {service_data['customer_id']} 不存在或无权访问")

        # 如果指定了设计方案，验证其存在性
        if service_data.get("design_plan_id"):
            design_plan = db.query(DesignPlan).filter(
                and_(
                    DesignPlan.id == service_data["design_plan_id"],
                    DesignPlan.user_id == user_id
                )
            ).first()

            if not design_plan:
                raise ValueError(f"设计方案 {service_data['design_plan_id']} 不存在或无权访问")

        # 创建服务记录
        service = ServiceRecord(
            user_id=user_id,
            **service_data
        )

        db.add(service)
        db.commit()
        db.refresh(service)

        logger.info(f"创建服务记录成功: ID={service.id}, customer_id={service.customer_id}")

        return service

    @staticmethod
    def complete_service(
        db: Session,
        service_id: int,
        completion_data: Dict[str, Any],
        user_id: int
    ) -> ServiceRecord:
        """
        完成服务记录

        Args:
            db: 数据库会话
            service_id: 服务记录ID
            completion_data: 完成数据（实际图、时长、材料、复盘等）
            user_id: 用户ID

        Returns:
            ServiceRecord: 更新后的服务记录

        Raises:
            ValueError: 服务记录不存在或无权访问
        """

        # 获取服务记录
        service = db.query(ServiceRecord).filter(
            and_(
                ServiceRecord.id == service_id,
                ServiceRecord.user_id == user_id
            )
        ).first()

        if not service:
            raise ValueError(f"服务记录 {service_id} 不存在或无权访问")

        # 更新字段
        for key, value in completion_data.items():
            if value is not None and hasattr(service, key):
                setattr(service, key, value)

        # 更新状态和完成时间
        service.status = "completed"
        service.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(service)

        logger.info(f"完成服务记录: ID={service_id}, 耗时={service.service_duration}分钟")

        return service

    @staticmethod
    def get_service_by_id(
        db: Session,
        service_id: int,
        user_id: int
    ) -> Optional[ServiceRecord]:
        """
        获取服务记录详情

        Args:
            db: 数据库会话
            service_id: 服务记录ID
            user_id: 用户ID

        Returns:
            ServiceRecord or None
        """

        service = db.query(ServiceRecord).filter(
            and_(
                ServiceRecord.id == service_id,
                ServiceRecord.user_id == user_id
            )
        ).first()

        return service

    @staticmethod
    def list_services(
        db: Session,
        user_id: int,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ServiceRecord]:
        """
        列出服务记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            customer_id: 过滤客户ID（可选）
            status: 过滤状态（可选）
            skip: 跳过记录数
            limit: 返回记录数上限

        Returns:
            服务记录列表
        """

        query = db.query(ServiceRecord).filter(ServiceRecord.user_id == user_id)

        if customer_id:
            query = query.filter(ServiceRecord.customer_id == customer_id)

        if status:
            query = query.filter(ServiceRecord.status == status)

        services = query.order_by(ServiceRecord.service_date.desc()).offset(skip).limit(limit).all()

        return services

    @staticmethod
    def update_service(
        db: Session,
        service_id: int,
        update_data: Dict[str, Any],
        user_id: int
    ) -> ServiceRecord:
        """
        更新服务记录

        Args:
            db: 数据库会话
            service_id: 服务记录ID
            update_data: 更新数据
            user_id: 用户ID

        Returns:
            ServiceRecord: 更新后的服务记录

        Raises:
            ValueError: 服务记录不存在或无权访问
        """

        service = db.query(ServiceRecord).filter(
            and_(
                ServiceRecord.id == service_id,
                ServiceRecord.user_id == user_id
            )
        ).first()

        if not service:
            raise ValueError(f"服务记录 {service_id} 不存在或无权访问")

        # 更新字段（排除 None 值）
        for key, value in update_data.items():
            if value is not None and hasattr(service, key):
                setattr(service, key, value)

        db.commit()
        db.refresh(service)

        logger.info(f"更新服务记录: ID={service_id}")

        return service

    @staticmethod
    def delete_service(
        db: Session,
        service_id: int,
        user_id: int
    ) -> bool:
        """
        删除服务记录

        Args:
            db: 数据库会话
            service_id: 服务记录ID
            user_id: 用户ID

        Returns:
            bool: 是否成功删除

        Raises:
            ValueError: 服务记录不存在或无权访问
        """

        service = db.query(ServiceRecord).filter(
            and_(
                ServiceRecord.id == service_id,
                ServiceRecord.user_id == user_id
            )
        ).first()

        if not service:
            raise ValueError(f"服务记录 {service_id} 不存在或无权访问")

        db.delete(service)
        db.commit()

        logger.info(f"删除服务记录: ID={service_id}")

        return True
