"""
能力维度业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional
import logging

from app.models.ability_dimension import AbilityDimension
from app.models.ability_record import AbilityRecord
from app.models.service_record import ServiceRecord

logger = logging.getLogger(__name__)


# 预设的 6 个核心能力维度
INITIAL_DIMENSIONS = [
    {
        "name": "颜色搭配",
        "name_en": "color_matching",
        "description": "评估色彩组合的和谐度和创意性",
        "scoring_criteria": "考察颜色的搭配是否协调、是否符合客户需求、是否具有创意",
        "display_order": 1,
        "is_active": 1
    },
    {
        "name": "图案精度",
        "name_en": "pattern_precision",
        "description": "评估图案的精确度和对称性",
        "scoring_criteria": "考察图案线条的清晰度、对称性、精细程度",
        "display_order": 2,
        "is_active": 1
    },
    {
        "name": "细节处理",
        "name_en": "detail_work",
        "description": "评估边缘处理、亮片分布等细节",
        "scoring_criteria": "考察边缘修整、装饰分布、细节完整度",
        "display_order": 3,
        "is_active": 1
    },
    {
        "name": "整体构图",
        "name_en": "composition",
        "description": "评估整体布局和视觉平衡",
        "scoring_criteria": "考察整体设计的美感、平衡感、视觉冲击力",
        "display_order": 4,
        "is_active": 1
    },
    {
        "name": "技法运用",
        "name_en": "technique_application",
        "description": "评估技法的熟练度和多样性",
        "scoring_criteria": "考察美甲技法的熟练程度、技法种类、创新运用",
        "display_order": 5,
        "is_active": 1
    },
    {
        "name": "创意表达",
        "name_en": "creative_expression",
        "description": "评估设计的原创性和艺术表现力",
        "scoring_criteria": "考察设计的创新性、独特性、艺术感染力",
        "display_order": 6,
        "is_active": 1
    }
]


class AbilityService:
    """能力维度服务"""

    @staticmethod
    def list_dimensions(
        db: Session,
        include_inactive: bool = False
    ) -> List[AbilityDimension]:
        """
        列出所有能力维度

        Args:
            db: 数据库会话
            include_inactive: 是否包含未启用的维度（默认 False）

        Returns:
            List[AbilityDimension]: 能力维度列表
        """
        query = db.query(AbilityDimension)

        # 过滤未启用的维度
        if not include_inactive:
            query = query.filter(AbilityDimension.is_active == 1)

        # 按显示顺序排序
        dimensions = query.order_by(AbilityDimension.display_order).all()

        return dimensions

    @staticmethod
    def get_dimension_by_id(
        db: Session,
        dimension_id: int
    ) -> Optional[AbilityDimension]:
        """
        根据 ID 获取能力维度

        Args:
            db: 数据库会话
            dimension_id: 维度 ID

        Returns:
            Optional[AbilityDimension]: 维度对象（不存在时返回 None）
        """
        dimension = db.query(AbilityDimension).filter(
            AbilityDimension.id == dimension_id
        ).first()

        return dimension

    @staticmethod
    def get_dimension_by_name(
        db: Session,
        name: str
    ) -> Optional[AbilityDimension]:
        """
        根据名称获取能力维度

        Args:
            db: 数据库会话
            name: 维度名称

        Returns:
            Optional[AbilityDimension]: 维度对象（不存在时返回 None）
        """
        dimension = db.query(AbilityDimension).filter(
            AbilityDimension.name == name
        ).first()

        return dimension

    @staticmethod
    def initialize_dimensions(db: Session) -> int:
        """
        初始化预设的 6 个能力维度

        Args:
            db: 数据库会话

        Returns:
            int: 创建的维度数量
        """
        created_count = 0

        for dim_data in INITIAL_DIMENSIONS:
            # 检查是否已存在
            existing = db.query(AbilityDimension).filter(
                AbilityDimension.name == dim_data["name"]
            ).first()

            if not existing:
                dimension = AbilityDimension(**dim_data)
                db.add(dimension)
                created_count += 1
                logger.info(f"创建能力维度: {dim_data['name']}")
            else:
                logger.info(f"能力维度已存在: {dim_data['name']}")

        db.commit()
        logger.info(f"能力维度初始化完成，新建 {created_count} 个维度")

        return created_count

    @staticmethod
    def get_ability_stats(
        db: Session,
        user_id: int
    ) -> Dict:
        """
        获取能力统计（雷达图数据）

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            Dict: 包含 dimensions、scores、avg_score、total_records
        """
        # 获取所有启用的维度
        dimensions = AbilityService.list_dimensions(db, include_inactive=False)

        if not dimensions:
            return {
                "dimensions": [],
                "scores": [],
                "avg_score": 0.0,
                "total_records": 0
            }

        dimension_names = []
        dimension_scores = []
        total_score = 0
        total_count = 0

        for dimension in dimensions:
            # 计算该维度的平均分
            avg_score = db.query(func.avg(AbilityRecord.score)).filter(
                AbilityRecord.user_id == user_id,
                AbilityRecord.dimension_id == dimension.id
            ).scalar()

            score = round(avg_score or 0, 1)
            dimension_names.append(dimension.name)
            dimension_scores.append(score)

            if avg_score:
                total_score += score
                total_count += 1

        # 计算总平均分
        avg_score = round(total_score / total_count, 1) if total_count > 0 else 0.0

        # 获取总记录数
        total_records = db.query(AbilityRecord).filter(
            AbilityRecord.user_id == user_id
        ).count()

        return {
            "dimensions": dimension_names,
            "scores": dimension_scores,
            "avg_score": avg_score,
            "total_records": total_records
        }

    @staticmethod
    def get_ability_summary(
        db: Session,
        user_id: int
    ) -> Dict:
        """
        获取能力总结（擅长/待提升）

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            Dict: 包含 strengths、improvements、total_services
        """
        # 获取能力统计
        stats = AbilityService.get_ability_stats(db, user_id)

        if not stats["dimensions"]:
            return {
                "strengths": [],
                "improvements": [],
                "total_services": 0
            }

        # 构建维度-分数列表
        dimension_scores = [
            {"dimension": dim, "score": score}
            for dim, score in zip(stats["dimensions"], stats["scores"])
        ]

        # 按分数排序
        sorted_scores = sorted(dimension_scores, key=lambda x: x["score"], reverse=True)

        # 获取总服务次数
        total_services = db.query(ServiceRecord).filter(
            ServiceRecord.user_id == user_id
        ).count()

        return {
            "strengths": sorted_scores[:3],  # 前3名（降序）
            "improvements": list(reversed(sorted_scores[-3:])),  # 后3名（反转为升序）
            "total_services": total_services
        }

    @staticmethod
    def get_ability_trend(
        db: Session,
        user_id: int,
        dimension_name: str,
        limit: int = 20
    ) -> Dict:
        """
        获取指定维度的能力成长趋势

        Args:
            db: 数据库会话
            user_id: 用户 ID
            dimension_name: 维度名称
            limit: 返回的最大记录数

        Returns:
            Dict: 包含 dimension_name 和 data_points
        """
        # 获取维度
        dimension = AbilityService.get_dimension_by_name(db, dimension_name)

        if not dimension:
            return {
                "dimension_name": dimension_name,
                "data_points": []
            }

        # 获取该维度的历史记录（按时间倒序）
        records = db.query(AbilityRecord).filter(
            AbilityRecord.user_id == user_id,
            AbilityRecord.dimension_id == dimension.id
        ).order_by(desc(AbilityRecord.created_at)).limit(limit).all()

        # 构建数据点
        data_points = [
            {
                "date": record.created_at,
                "score": record.score,
                "service_record_id": record.service_record_id
            }
            for record in reversed(records)  # 反转为时间升序
        ]

        return {
            "dimension_name": dimension_name,
            "data_points": data_points
        }
