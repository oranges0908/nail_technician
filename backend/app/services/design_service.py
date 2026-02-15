"""
设计方案业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
import datetime
import logging

from app.models.design_plan import DesignPlan
from app.models.customer import Customer
from app.schemas.design import (
    DesignGenerateRequest,
    DesignRefineRequest,
    DesignPlanUpdate,
)
from app.services.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class DesignService:
    """设计方案服务"""

    @staticmethod
    async def generate_design(
        db: Session,
        design_request: DesignGenerateRequest,
        user_id: int
    ) -> DesignPlan:
        """
        生成设计方案（调用AI）

        Args:
            db: 数据库会话
            design_request: 设计生成请求
            user_id: 所属美甲师ID

        Returns:
            DesignPlan: 创建的设计方案对象

        Raises:
            HTTPException: 客户不存在或AI调用失败时抛出错误
        """
        # 验证客户是否存在（如果提供了customer_id）
        if design_request.customer_id:
            customer = db.query(Customer).filter(
                and_(
                    Customer.id == design_request.customer_id,
                    Customer.user_id == user_id
                )
            ).first()

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"客户 ID {design_request.customer_id} 不存在"
                )

        try:
            # 获取AI Provider
            ai_provider = AIProviderFactory.get_provider()

            # 调用AI生成设计图
            logger.info(f"调用AI生成设计，提示词: {design_request.prompt[:50]}...")
            generated_image_url = await ai_provider.generate_design(
                prompt=design_request.prompt,
                reference_images=design_request.reference_images,
                design_target=design_request.design_target
            )
            logger.info(f"AI生成成功，图片URL: {generated_image_url}")

            # 调用AI估算执行难度
            logger.info("调用AI估算执行难度...")
            estimation = await ai_provider.estimate_execution(
                design_image=generated_image_url
            )
            logger.info(f"AI估算成功: {estimation}")

            # 创建设计方案记录
            design_plan = DesignPlan(
                user_id=user_id,
                customer_id=design_request.customer_id,
                ai_prompt=design_request.prompt,
                generated_image_path=generated_image_url,
                model_version="dall-e-3",
                design_target=design_request.design_target,
                style_keywords=design_request.style_keywords,
                reference_images=design_request.reference_images,
                version=1,
                estimated_duration=estimation.get("estimated_duration"),
                estimated_materials=estimation.get("materials"),
                difficulty_level=estimation.get("difficulty_level"),
                title=design_request.title,
                notes=design_request.notes,
                is_archived=0
            )

            db.add(design_plan)
            db.commit()
            db.refresh(design_plan)

            logger.info(f"设计方案创建成功，ID: {design_plan.id}")
            return design_plan

        except Exception as e:
            logger.error(f"AI生成设计失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI生成设计失败: {str(e)}"
            )

    @staticmethod
    async def refine_design(
        db: Session,
        design_id: int,
        refine_request: DesignRefineRequest,
        user_id: int
    ) -> DesignPlan:
        """
        优化设计方案（调用AI，创建新版本）

        Args:
            db: 数据库会话
            design_id: 原设计方案ID
            refine_request: 优化请求
            user_id: 所属美甲师ID

        Returns:
            DesignPlan: 新创建的设计方案对象

        Raises:
            HTTPException: 原设计不存在或AI调用失败时抛出错误
        """
        # 获取原设计方案
        original_design = DesignService.get_design_by_id(
            db, design_id, user_id
        )

        if not original_design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设计方案 ID {design_id} 不存在"
            )

        try:
            # 获取AI Provider
            ai_provider = AIProviderFactory.get_provider()

            # 调用AI优化设计
            logger.info(f"调用AI优化设计 ID {design_id}，指令: {refine_request.refinement_instruction}")
            refined_image_url = await ai_provider.refine_design(
                original_image=original_design.generated_image_path,
                refinement_instruction=refine_request.refinement_instruction,
                design_target=original_design.design_target or "10nails"
            )
            logger.info(f"AI优化成功，图片URL: {refined_image_url}")

            # 调用AI估算执行难度
            logger.info("调用AI估算执行难度...")
            estimation = await ai_provider.estimate_execution(
                design_image=refined_image_url
            )
            logger.info(f"AI估算成功: {estimation}")

            # 创建新版本设计方案
            new_design = DesignPlan(
                user_id=user_id,
                customer_id=original_design.customer_id,
                ai_prompt=original_design.ai_prompt,
                generated_image_path=refined_image_url,
                model_version="dall-e-3",
                design_target=original_design.design_target,
                style_keywords=original_design.style_keywords,
                reference_images=original_design.reference_images,
                parent_design_id=original_design.id,
                version=original_design.version + 1,
                refinement_instruction=refine_request.refinement_instruction,
                estimated_duration=estimation.get("estimated_duration"),
                estimated_materials=estimation.get("materials"),
                difficulty_level=estimation.get("difficulty_level"),
                title=original_design.title,
                notes=original_design.notes,
                is_archived=0
            )

            db.add(new_design)
            db.commit()
            db.refresh(new_design)

            logger.info(f"优化设计方案创建成功，ID: {new_design.id}, 版本: {new_design.version}")
            return new_design

        except Exception as e:
            logger.error(f"AI优化设计失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI优化设计失败: {str(e)}"
            )

    @staticmethod
    def get_design_by_id(
        db: Session,
        design_id: int,
        user_id: int
    ) -> Optional[DesignPlan]:
        """
        根据ID获取设计方案

        Args:
            db: 数据库会话
            design_id: 设计方案ID
            user_id: 所属美甲师ID

        Returns:
            Optional[DesignPlan]: 设计方案对象（不存在时返回None）
        """
        design = db.query(DesignPlan).filter(
            and_(
                DesignPlan.id == design_id,
                DesignPlan.user_id == user_id
            )
        ).first()

        return design

    @staticmethod
    def list_designs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        is_archived: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[DesignPlan], int]:
        """
        列出设计方案（支持分页、过滤、搜索）

        Args:
            db: 数据库会话
            user_id: 所属美甲师ID
            skip: 跳过的记录数
            limit: 返回的最大记录数
            customer_id: 客户ID过滤
            is_archived: 归档状态过滤（0=未归档，1=已归档）
            search: 搜索关键词（在标题、提示词中搜索）

        Returns:
            Tuple[List[DesignPlan], int]: (设计方案列表, 总数)
        """
        # 基础查询
        query = db.query(DesignPlan).filter(
            DesignPlan.user_id == user_id
        )

        # 客户过滤
        if customer_id is not None:
            query = query.filter(DesignPlan.customer_id == customer_id)

        # 归档状态过滤
        if is_archived is not None:
            query = query.filter(DesignPlan.is_archived == is_archived)

        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    DesignPlan.title.like(search_pattern),
                    DesignPlan.ai_prompt.like(search_pattern)
                )
            )

        # 获取总数
        total = query.count()

        # 分页并按创建时间倒序排序
        designs = query.order_by(
            desc(DesignPlan.created_at)
        ).offset(skip).limit(limit).all()

        return designs, total

    @staticmethod
    def update_design(
        db: Session,
        design_id: int,
        user_id: int,
        update_data: DesignPlanUpdate
    ) -> Optional[DesignPlan]:
        """
        更新设计方案

        Args:
            db: 数据库会话
            design_id: 设计方案ID
            user_id: 所属美甲师ID
            update_data: 更新数据

        Returns:
            Optional[DesignPlan]: 更新后的设计方案对象（不存在时返回None）
        """
        # 查找设计方案
        design = DesignService.get_design_by_id(
            db, design_id, user_id
        )

        if not design:
            return None

        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(design, key, value)

        db.commit()
        db.refresh(design)

        return design

    @staticmethod
    def archive_design(
        db: Session,
        design_id: int,
        user_id: int
    ) -> Optional[DesignPlan]:
        """
        归档设计方案

        Args:
            db: 数据库会话
            design_id: 设计方案ID
            user_id: 所属美甲师ID

        Returns:
            Optional[DesignPlan]: 归档后的设计方案对象（不存在时返回None）
        """
        # 查找设计方案
        design = DesignService.get_design_by_id(
            db, design_id, user_id
        )

        if not design:
            return None

        # 归档
        design.is_archived = 1

        db.commit()
        db.refresh(design)

        return design

    @staticmethod
    def delete_design(
        db: Session,
        design_id: int,
        user_id: int
    ) -> bool:
        """
        删除设计方案

        Args:
            db: 数据库会话
            design_id: 设计方案ID
            user_id: 所属美甲师ID

        Returns:
            bool: 删除成功返回True，不存在返回False
        """
        # 查找设计方案
        design = DesignService.get_design_by_id(
            db, design_id, user_id
        )

        if not design:
            return False

        db.delete(design)
        db.commit()

        return True

    @staticmethod
    def get_design_versions(
        db: Session,
        design_id: int,
        user_id: int
    ) -> List[DesignPlan]:
        """
        获取设计方案的版本历史

        Args:
            db: 数据库会话
            design_id: 设计方案ID
            user_id: 所属美甲师ID

        Returns:
            List[DesignPlan]: 版本历史列表（按版本号升序）
        """
        # 获取指定设计
        design = DesignService.get_design_by_id(
            db, design_id, user_id
        )

        if not design:
            return []

        # 如果是子版本，先找到根版本
        root_id = design.parent_design_id or design.id

        # 查询所有版本（包括根版本和所有子版本）
        versions = db.query(DesignPlan).filter(
            and_(
                DesignPlan.user_id == user_id,
                or_(
                    DesignPlan.id == root_id,
                    DesignPlan.parent_design_id == root_id
                )
            )
        ).order_by(DesignPlan.version).all()

        return versions

    @staticmethod
    def get_recent_designs(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[DesignPlan]:
        """
        获取最近创建的设计方案

        Args:
            db: 数据库会话
            user_id: 所属美甲师ID
            limit: 返回的最大记录数

        Returns:
            List[DesignPlan]: 最近设计方案列表
        """
        designs = db.query(DesignPlan).filter(
            and_(
                DesignPlan.user_id == user_id,
                DesignPlan.is_archived == 0
            )
        ).order_by(
            desc(DesignPlan.created_at)
        ).limit(limit).all()

        return designs
