"""
灵感图库业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
import datetime

from app.models.inspiration_image import InspirationImage
from app.schemas.inspiration import (
    InspirationImageCreate,
    InspirationImageUpdate,
)


class InspirationService:
    """灵感图库服务"""

    @staticmethod
    def create_inspiration(
        db: Session,
        inspiration_data: InspirationImageCreate,
        user_id: int
    ) -> InspirationImage:
        """
        创建灵感图

        Args:
            db: 数据库会话
            inspiration_data: 灵感图创建数据
            user_id: 所属美甲师ID

        Returns:
            InspirationImage: 创建的灵感图对象
        """
        # 创建灵感图
        inspiration = InspirationImage(
            **inspiration_data.model_dump(),
            user_id=user_id,
            usage_count=0
        )

        db.add(inspiration)
        db.commit()
        db.refresh(inspiration)

        return inspiration

    @staticmethod
    def get_inspiration_by_id(
        db: Session,
        inspiration_id: int,
        user_id: int
    ) -> Optional[InspirationImage]:
        """
        根据ID获取灵感图

        Args:
            db: 数据库会话
            inspiration_id: 灵感图ID
            user_id: 所属美甲师ID

        Returns:
            Optional[InspirationImage]: 灵感图对象（不存在时返回None）
        """
        inspiration = db.query(InspirationImage).filter(
            and_(
                InspirationImage.id == inspiration_id,
                InspirationImage.user_id == user_id
            )
        ).first()

        return inspiration

    @staticmethod
    def list_inspirations(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> Tuple[List[InspirationImage], int]:
        """
        列出灵感图（支持分页、过滤、搜索）

        Args:
            db: 数据库会话
            user_id: 所属美甲师ID
            skip: 跳过的记录数
            limit: 返回的最大记录数
            category: 分类过滤
            tags: 标签过滤（包含任一标签即返回）
            search: 搜索关键词（在标题、描述中搜索）

        Returns:
            Tuple[List[InspirationImage], int]: (灵感图列表, 总数)
        """
        # 基础查询
        query = db.query(InspirationImage).filter(
            InspirationImage.user_id == user_id
        )

        # 分类过滤
        if category:
            query = query.filter(InspirationImage.category == category)

        # 标签过滤（JSON 数组包含任一标签）
        if tags and len(tags) > 0:
            # SQLite JSON 查询需要特殊处理
            # 使用 OR 条件组合多个标签
            tag_conditions = []
            for tag in tags:
                # 使用 JSON_EXTRACT 或字符串包含来检查
                tag_conditions.append(
                    func.json_extract(InspirationImage.tags, '$').contains(f'"{tag}"')
                )
            if tag_conditions:
                query = query.filter(or_(*tag_conditions))

        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    InspirationImage.title.like(search_pattern),
                    InspirationImage.description.like(search_pattern)
                )
            )

        # 获取总数
        total = query.count()

        # 分页并按创建时间倒序排序
        inspirations = query.order_by(
            InspirationImage.created_at.desc()
        ).offset(skip).limit(limit).all()

        return inspirations, total

    @staticmethod
    def update_inspiration(
        db: Session,
        inspiration_id: int,
        user_id: int,
        update_data: InspirationImageUpdate
    ) -> Optional[InspirationImage]:
        """
        更新灵感图

        Args:
            db: 数据库会话
            inspiration_id: 灵感图ID
            user_id: 所属美甲师ID
            update_data: 更新数据

        Returns:
            Optional[InspirationImage]: 更新后的灵感图对象（不存在时返回None）
        """
        # 查找灵感图
        inspiration = InspirationService.get_inspiration_by_id(
            db, inspiration_id, user_id
        )

        if not inspiration:
            return None

        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(inspiration, key, value)

        db.commit()
        db.refresh(inspiration)

        return inspiration

    @staticmethod
    def delete_inspiration(
        db: Session,
        inspiration_id: int,
        user_id: int
    ) -> bool:
        """
        删除灵感图

        Args:
            db: 数据库会话
            inspiration_id: 灵感图ID
            user_id: 所属美甲师ID

        Returns:
            bool: 删除成功返回True，不存在返回False
        """
        # 查找灵感图
        inspiration = InspirationService.get_inspiration_by_id(
            db, inspiration_id, user_id
        )

        if not inspiration:
            return False

        db.delete(inspiration)
        db.commit()

        return True

    @staticmethod
    def increment_usage_count(
        db: Session,
        inspiration_id: int,
        user_id: int
    ) -> Optional[InspirationImage]:
        """
        增加灵感图使用次数

        Args:
            db: 数据库会话
            inspiration_id: 灵感图ID
            user_id: 所属美甲师ID

        Returns:
            Optional[InspirationImage]: 更新后的灵感图对象（不存在时返回None）
        """
        # 查找灵感图
        inspiration = InspirationService.get_inspiration_by_id(
            db, inspiration_id, user_id
        )

        if not inspiration:
            return None

        # 增加使用次数
        inspiration.usage_count += 1
        inspiration.last_used_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(inspiration)

        return inspiration

    @staticmethod
    def get_popular_inspirations(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[InspirationImage]:
        """
        获取热门灵感图（按使用次数排序）

        Args:
            db: 数据库会话
            user_id: 所属美甲师ID
            limit: 返回的最大记录数

        Returns:
            List[InspirationImage]: 热门灵感图列表
        """
        inspirations = db.query(InspirationImage).filter(
            InspirationImage.user_id == user_id
        ).order_by(
            InspirationImage.usage_count.desc(),
            InspirationImage.created_at.desc()
        ).limit(limit).all()

        return inspirations

    @staticmethod
    def get_recent_inspirations(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[InspirationImage]:
        """
        获取最近添加的灵感图

        Args:
            db: 数据库会话
            user_id: 所属美甲师ID
            limit: 返回的最大记录数

        Returns:
            List[InspirationImage]: 最近灵感图列表
        """
        inspirations = db.query(InspirationImage).filter(
            InspirationImage.user_id == user_id
        ).order_by(
            InspirationImage.created_at.desc()
        ).limit(limit).all()

        return inspirations
