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
    """AI Analysis Service"""

    @staticmethod
    async def analyze_service(db: Session, service_record_id: int) -> ComparisonResult:
        """
        Run comprehensive AI analysis on a service record (image + text)

        Args:
            db: Database session
            service_record_id: Service record ID

        Returns:
            ComparisonResult: Comparison analysis result

        Raises:
            ValueError: Service record not found, missing required info, etc.
        """

        # 1. Get service record
        service = db.query(ServiceRecord).filter(ServiceRecord.id == service_record_id).first()
        if not service:
            raise ValueError(f"Service record {service_record_id} not found")

        if not service.actual_image_path:
            raise ValueError("Service record is missing the actual completed photo")

        if not service.design_plan_id:
            raise ValueError("Service record is not linked to a design plan")

        # 2. Get design plan image
        design_plan = service.design_plan
        if not design_plan or not design_plan.generated_image_path:
            raise ValueError("Design plan is missing its generated image")

        design_image_url = design_plan.generated_image_path
        actual_image_url = service.actual_image_path

        # 3. Call AI Provider for comprehensive analysis
        ai_provider = AIProviderFactory.get_provider()

        logger.info(f"Starting AI comprehensive analysis, service record ID: {service_record_id}")
        logger.info(f"Text context included: artist_review={bool(service.artist_review)}, "
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
            logger.error(f"AI analysis failed: {e}")
            raise ValueError(f"AI analysis failed: {str(e)}")

        # 4. Save or update comparison result
        comparison = db.query(ComparisonResult).filter(
            ComparisonResult.service_record_id == service_record_id
        ).first()

        if comparison:
            # Update existing record
            comparison.similarity_score = analysis_result["similarity_score"]
            comparison.differences = analysis_result.get("differences", {})
            comparison.suggestions = analysis_result.get("suggestions", [])
            comparison.contextual_insights = analysis_result.get("contextual_insights", {})
        else:
            # Create new record
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

        # 5. Update ability records
        if "ability_scores" in analysis_result:
            await AnalysisService._update_ability_records(
                db=db,
                service_record_id=service_record_id,
                user_id=service.user_id,
                ability_scores=analysis_result["ability_scores"]
            )

        # 6. Update customer preference profile
        if service.customer_id:
            await AnalysisService._update_customer_profile(
                db=db,
                customer_id=service.customer_id,
                analysis_result=analysis_result
            )

        logger.info(f"AI comprehensive analysis complete, similarity: {analysis_result['similarity_score']}")

        return comparison

    @staticmethod
    async def _update_ability_records(
        db: Session,
        service_record_id: int,
        user_id: int,
        ability_scores: Dict[str, Dict]
    ):
        """
        Update ability records

        Args:
            db: Database session
            service_record_id: Service record ID
            user_id: User ID
            ability_scores: Ability scores dict
                {
                    "color_matching": {"score": 85, "evidence": "..."},
                    "pattern_precision": {"score": 90, "evidence": "..."}
                }
        """

        # Delete existing ability records (if re-analyzing)
        db.query(AbilityRecord).filter(
            AbilityRecord.service_record_id == service_record_id
        ).delete()

        # Create new ability records
        for dimension_name, score_data in ability_scores.items():
            # Find or create ability dimension
            dimension = db.query(AbilityDimension).filter(
                AbilityDimension.name == dimension_name
            ).first()

            if not dimension:
                # Auto-create new dimension
                dimension = AbilityDimension(
                    name=dimension_name,
                    name_en=dimension_name.lower().replace(" ", "_"),
                    description=f"Auto-created dimension: {dimension_name}"
                )
                db.add(dimension)
                db.flush()

            # Create ability record
            ability_record = AbilityRecord(
                user_id=user_id,
                service_record_id=service_record_id,
                dimension_id=dimension.id,
                score=score_data["score"],
                evidence=score_data.get("evidence", "")
            )
            db.add(ability_record)

        db.commit()

        logger.info(f"Ability records updated, {len(ability_scores)} dimensions")

    @staticmethod
    async def _update_customer_profile(db: Session, customer_id: int, analysis_result: dict):
        """Incrementally update customer preference profile (colors, styles, notes)"""
        from app.models.customer_profile import CustomerProfile
        customer_updates = analysis_result.get("customer_updates", {})
        if not customer_updates:
            return
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == customer_id
        ).first()
        if not profile:
            profile = CustomerProfile(customer_id=customer_id)
            db.add(profile)
        # append_unique colors
        if "colors" in customer_updates:
            existing = list(profile.color_preferences or [])
            for c in customer_updates["colors"]:
                if c and c not in existing:
                    existing.append(c)
            profile.color_preferences = existing
        # append_unique styles
        if "styles" in customer_updates:
            existing = list(profile.style_preferences or [])
            for s in customer_updates["styles"]:
                if s and s not in existing:
                    existing.append(s)
            profile.style_preferences = existing
        # append_unique notes → pattern_preferences (semicolon-separated)
        if "notes" in customer_updates:
            existing = profile.pattern_preferences or ""
            for note in customer_updates["notes"]:
                if note and note not in existing:
                    existing = (existing + "; " + note).strip("; ")
            profile.pattern_preferences = existing
        db.commit()
        logger.info(f"Customer profile incrementally updated, customer_id: {customer_id}")

    @staticmethod
    def get_ability_trend(
        db: Session,
        user_id: int,
        dimension_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get ability trend data

        Args:
            db: Database session
            user_id: User ID
            dimension_name: Dimension name
            limit: Number of records to return

        Returns:
            List of trend data
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
            for r in reversed(records)  # chronological order
        ]

        return trend_data

    @staticmethod
    def get_ability_radar(
        db: Session,
        user_id: int
    ) -> Dict:
        """
        Get ability radar chart data (scores across dimensions from the most recent service)

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Radar chart data
        """

        # Get most recent service record
        latest_service = db.query(ServiceRecord).filter(
            ServiceRecord.user_id == user_id,
            ServiceRecord.status == "completed"
        ).order_by(ServiceRecord.completed_at.desc()).first()

        if not latest_service:
            return {"dimensions": [], "scores": []}

        # Get all ability records for this service
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
