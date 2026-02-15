import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.service_record import ServiceRecord
from app.models.comparison_result import ComparisonResult
from app.models.ability_record import AbilityRecord
from app.models.ability_dimension import AbilityDimension
from app.services.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class AnalysisService:
    """AI 分析服务"""

    @staticmethod
    async def analyze_service(db: Session, service_record_id: int) -> ComparisonResult:
        """
        对服务记录进行 AI 综合分析（图片 + 文本）

        Args:
            db: 数据库会话
            service_record_id: 服务记录 ID

        Returns:
            ComparisonResult: 对比分析结果

        Raises:
            ValueError: 服务记录不存在、缺少必要信息等
        """

        # 1. 获取服务记录
        service = db.query(ServiceRecord).filter(ServiceRecord.id == service_record_id).first()
        if not service:
            raise ValueError(f"服务记录 {service_record_id} 不存在")

        if not service.actual_image_path:
            raise ValueError("服务记录缺少实际完成图")

        if not service.design_plan_id:
            raise ValueError("服务记录未关联设计方案")

        # 2. 获取设计方案图片
        design_plan = service.design_plan
        if not design_plan or not design_plan.generated_image_path:
            raise ValueError("设计方案缺少生成图片")

        # 直接使用存储的路径（如 /uploads/designs/xxx.png）
        # AI Provider 的 _load_image_part 会处理路径转换
        design_image_url = design_plan.generated_image_path
        actual_image_url = service.actual_image_path

        # 3. 调用 AI Provider 进行综合分析
        ai_provider = AIProviderFactory.get_provider()

        logger.info(f"开始 AI 综合分析，服务记录 ID: {service_record_id}")
        logger.info(f"包含文本上下文: artist_review={bool(service.artist_review)}, "
                   f"customer_feedback={bool(service.customer_feedback)}, "
                   f"satisfaction={service.customer_satisfaction}")

        try:
            analysis_result = await ai_provider.compare_images(
                design_image=design_image_url,
                actual_image=actual_image_url,
                artist_review=service.artist_review,
                customer_feedback=service.customer_feedback,
                customer_satisfaction=service.customer_satisfaction
            )
        except Exception as e:
            logger.error(f"AI 分析失败: {e}")
            raise ValueError(f"AI 分析失败: {str(e)}")

        # 4. 保存或更新对比结果
        comparison = db.query(ComparisonResult).filter(
            ComparisonResult.service_record_id == service_record_id
        ).first()

        if comparison:
            # 更新现有记录
            comparison.similarity_score = analysis_result["similarity_score"]
            comparison.differences = analysis_result.get("differences", {})
            comparison.suggestions = analysis_result.get("suggestions", [])
            comparison.contextual_insights = analysis_result.get("contextual_insights", {})
        else:
            # 创建新记录
            comparison = ComparisonResult(
                service_record_id=service_record_id,
                similarity_score=analysis_result["similarity_score"],
                differences=analysis_result.get("differences", {}),
                suggestions=analysis_result.get("suggestions", []),
                contextual_insights=analysis_result.get("contextual_insights", {})
            )
            db.add(comparison)

        db.commit()
        db.refresh(comparison)

        # 5. 更新能力记录
        if "ability_scores" in analysis_result:
            await AnalysisService._update_ability_records(
                db=db,
                service_record_id=service_record_id,
                user_id=service.user_id,
                ability_scores=analysis_result["ability_scores"]
            )

        logger.info(f"AI 综合分析完成，相似度: {analysis_result['similarity_score']}")

        return comparison

    @staticmethod
    async def _update_ability_records(
        db: Session,
        service_record_id: int,
        user_id: int,
        ability_scores: Dict[str, Dict]
    ):
        """
        更新能力记录

        Args:
            db: 数据库会话
            service_record_id: 服务记录ID
            user_id: 用户ID
            ability_scores: 能力评分字典
                {
                    "颜色搭配": {"score": 85, "evidence": "..."},
                    "图案精度": {"score": 90, "evidence": "..."}
                }
        """

        # 删除现有的能力记录（如果重新分析）
        db.query(AbilityRecord).filter(
            AbilityRecord.service_record_id == service_record_id
        ).delete()

        # 创建新的能力记录
        for dimension_name, score_data in ability_scores.items():
            # 查找或创建能力维度
            dimension = db.query(AbilityDimension).filter(
                AbilityDimension.name == dimension_name
            ).first()

            if not dimension:
                # 自动创建新维度
                dimension = AbilityDimension(
                    name=dimension_name,
                    name_en=dimension_name.lower().replace(" ", "_"),
                    description=f"自动创建的维度: {dimension_name}"
                )
                db.add(dimension)
                db.flush()

            # 创建能力记录
            ability_record = AbilityRecord(
                user_id=user_id,
                service_record_id=service_record_id,
                dimension_id=dimension.id,
                score=score_data["score"],
                evidence=score_data.get("evidence", "")
            )
            db.add(ability_record)

        db.commit()

        logger.info(f"更新能力记录完成，共 {len(ability_scores)} 个维度")

    @staticmethod
    def get_ability_trend(
        db: Session,
        user_id: int,
        dimension_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        获取能力趋势数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            dimension_name: 维度名称
            limit: 返回记录数

        Returns:
            趋势数据列表
        """

        dimension = db.query(AbilityDimension).filter(
            AbilityDimension.name == dimension_name
        ).first()

        if not dimension:
            return []

        records = db.query(AbilityRecord).filter(
            AbilityRecord.user_id == user_id,
            AbilityRecord.dimension_id == dimension.id
        ).order_by(AbilityRecord.created_at.desc()).limit(limit).all()

        trend_data = [
            {
                "service_record_id": r.service_record_id,
                "score": r.score,
                "evidence": r.evidence,
                "created_at": r.created_at.isoformat()
            }
            for r in reversed(records)  # 按时间正序排列
        ]

        return trend_data

    @staticmethod
    def get_ability_radar(
        db: Session,
        user_id: int
    ) -> Dict:
        """
        获取能力雷达图数据（最近一次服务的各维度评分）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            雷达图数据
        """

        # 获取最近一次服务记录
        latest_service = db.query(ServiceRecord).filter(
            ServiceRecord.user_id == user_id,
            ServiceRecord.status == "completed"
        ).order_by(ServiceRecord.completed_at.desc()).first()

        if not latest_service:
            return {"dimensions": [], "scores": []}

        # 获取该服务的所有能力记录
        ability_records = db.query(AbilityRecord).join(AbilityDimension).filter(
            AbilityRecord.service_record_id == latest_service.id
        ).all()

        radar_data = {
            "dimensions": [r.dimension.name for r in ability_records],
            "scores": [r.score for r in ability_records],
            "service_record_id": latest_service.id,
            "service_date": latest_service.service_date.isoformat()
        }

        return radar_data
