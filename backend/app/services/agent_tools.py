"""
AI Agent Tool Registry
Wraps existing business Service methods as OpenAI Function Calling format tools.
"""
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.conversation_session import ConversationSession
from app.models.inspiration_image import InspirationImage
from app.services.customer_service import CustomerService
from app.services.design_service import DesignService
from app.services.service_record_service import ServiceRecordService
from app.services.analysis_service import AnalysisService
from app.services.ability_service import AbilityService
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.design import DesignGenerateRequest, DesignRefineRequest

logger = logging.getLogger(__name__)


# ── OpenAI Function Calling 工具定义 ───────────────────────────────────────

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "search_customer",
            "description": "Search existing customers by name or phone number, returns matching list",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Name or phone number keyword"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_customer",
            "description": "Create a new customer profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "email": {"type": "string", "description": "Email (optional)"},
                    "notes": {"type": "string", "description": "Notes (optional)"}
                },
                "required": ["name", "phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_detail",
            "description": "Get detailed information for a specific customer (including profile)",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "Customer ID"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_design",
            "description": "Call AI to generate a nail design image. Takes about 30-60 seconds; inform user it is processing before calling",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Design description including style, colors, patterns, etc."
                    },
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID (optional, used to read customer preferences)"
                    },
                    "reference_images": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of reference image paths (optional)"
                    },
                    "style_keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of style keywords (optional)"
                    },
                    "design_target": {
                        "type": "string",
                        "enum": ["single", "5nails", "10nails"],
                        "description": "Design target (default: 10nails)"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refine_design",
            "description": "AI iterative refinement of an existing design, generates a new version",
            "parameters": {
                "type": "object",
                "properties": {
                    "design_id": {
                        "type": "integer",
                        "description": "ID of the design to refine"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Refinement instruction, e.g. 'change to a deeper pink' or 'remove diamond decoration'"
                    }
                },
                "required": ["design_id", "instruction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_service_record",
            "description": "Create today's service record, linking customer and design plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID"
                    },
                    "design_plan_id": {
                        "type": "integer",
                        "description": "Design plan ID (optional)"
                    },
                    "service_date": {
                        "type": "string",
                        "description": "Service date in YYYY-MM-DD format (defaults to today)"
                    }
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_service",
            "description": "Complete service record, upload actual photo, record duration and review",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "integer",
                        "description": "Service record ID"
                    },
                    "actual_image_path": {
                        "type": "string",
                        "description": "Actual photo path (path already uploaded to server)"
                    },
                    "service_duration": {
                        "type": "integer",
                        "description": "Service duration in minutes"
                    },
                    "materials_used": {
                        "type": "string",
                        "description": "Materials used description (optional)"
                    },
                    "artist_review": {
                        "type": "string",
                        "description": "Nail artist's review/reflection (optional)"
                    },
                    "customer_feedback": {
                        "type": "string",
                        "description": "Customer feedback (optional)"
                    },
                    "customer_satisfaction": {
                        "type": "integer",
                        "description": "Customer satisfaction 1-5 (optional)"
                    }
                },
                "required": ["service_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_analysis",
            "description": "Run AI comparison analysis on completed service record (design vs actual photo), generates 6-dimension scores. Takes 20-40 seconds",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "integer",
                        "description": "Service record ID"
                    }
                },
                "required": ["service_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ability_summary",
            "description": "Get nail artist's ability analysis summary, including strengths and dimensions to improve",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_inspirations",
            "description": "Search inspiration image library, returns list of available reference images",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search keyword (title/tag, optional)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category filter (optional)"
                    }
                },
                "required": []
            }
        }
    }
]


# ── 工具执行器 ──────────────────────────────────────────────────────────────

class ToolExecutor:
    """
    Routes tool calls to corresponding existing Service methods.
    If new business IDs are produced after execution, updates session.context and persists to DB.
    """

    async def execute(
        self,
        tool_name: str,
        tool_args: dict,
        db: Session,
        user_id: int,
        session: ConversationSession
    ) -> str:
        """Execute tool, return LLM-friendly JSON string"""
        handler = getattr(self, f"_tool_{tool_name}", None)
        if not handler:
            return json.dumps(
                {"error": f"Unknown tool: {tool_name}"},
                ensure_ascii=False
            )
        try:
            return await handler(
                db=db, user_id=user_id, session=session, **tool_args
            )
        except Exception as e:
            logger.error(f"Tool execution failed {tool_name}: {e}", exc_info=True)
            detail = getattr(e, "detail", None) or str(e)
            return json.dumps(
                {"error": f"Tool execution failed: {detail}"},
                ensure_ascii=False
            )

    async def _tool_search_customer(self, db, user_id, session, query):
        customers, total = CustomerService.list_customers(
            db, user_id, search=query, limit=5
        )
        if total == 0:
            return json.dumps(
                {"result": "No matching customers found", "total": 0, "customers": []},
                ensure_ascii=False
            )
        data = []
        for c in customers:
            data.append({
                "id": c.id,
                "name": c.name,
                "phone": c.phone or "",
                "notes": c.notes or ""
            })
        # 唯一匹配时自动写入 context
        if total == 1:
            ctx = dict(session.context or {})
            ctx["customer_id"] = customers[0].id
            ctx["customer_name"] = customers[0].name
            session.context = ctx
            db.commit()
        return json.dumps(
            {"result": "Found the following customers", "total": total, "customers": data},
            ensure_ascii=False
        )

    async def _tool_create_customer(self, db, user_id, session,
                                    name, phone, email=None, notes=None):
        customer_data = CustomerCreate(
            name=name,
            phone=phone,
            email=email,
            notes=notes
        )
        customer = CustomerService.create_customer(db, customer_data, user_id)
        # 更新 session.context
        ctx = dict(session.context or {})
        ctx["customer_id"] = customer.id
        ctx["customer_name"] = customer.name
        session.context = ctx
        db.commit()
        return json.dumps({
            "result": "Customer created successfully",
            "customer_id": customer.id,
            "name": customer.name,
            "phone": customer.phone
        }, ensure_ascii=False)

    async def _tool_get_customer_detail(self, db, user_id, session, customer_id):
        customer = CustomerService.get_customer_by_id(db, customer_id, user_id)
        if not customer:
            return json.dumps(
                {"error": f"Customer ID {customer_id} not found"},
                ensure_ascii=False
            )
        profile = customer.profile
        profile_data = {}
        if profile:
            profile_data = {
                "nail_shape": profile.nail_shape,
                "nail_length": profile.nail_length,
                "color_preferences": profile.color_preferences,
                "style_preferences": profile.style_preferences,
                "allergies": profile.allergies,
                "prohibitions": profile.prohibitions,
            }
        return json.dumps({
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "notes": customer.notes,
            "profile": profile_data
        }, ensure_ascii=False)

    async def _tool_generate_design(self, db, user_id, session, prompt,
                                    customer_id=None, reference_images=None,
                                    style_keywords=None, design_target="10nails"):
        ctx = dict(session.context or {})
        effective_customer_id = customer_id or ctx.get("customer_id")
        effective_refs = reference_images or ctx.get("inspiration_paths", [])

        req = DesignGenerateRequest(
            prompt=prompt,
            customer_id=effective_customer_id,
            reference_images=effective_refs,
            style_keywords=style_keywords,
            design_target=design_target
        )
        design = await DesignService.generate_design(db, req, user_id)

        # 更新 session.context
        ctx["design_plan_id"] = design.id
        ctx["design_image_url"] = design.generated_image_path
        session.context = ctx
        db.commit()

        return json.dumps({
            "result": "Design generated successfully",
            "design_id": design.id,
            "image_url": design.generated_image_path,
            "estimated_duration": design.estimated_duration,
            "difficulty_level": design.difficulty_level,
            "estimated_materials": design.estimated_materials
        }, ensure_ascii=False)

    async def _tool_refine_design(self, db, user_id, session, design_id, instruction):
        from app.schemas.design import DesignRefineRequest
        req = DesignRefineRequest(refinement_instruction=instruction)
        new_design = await DesignService.refine_design(db, design_id, req, user_id)

        # 更新 session.context
        ctx = dict(session.context or {})
        ctx["design_plan_id"] = new_design.id
        ctx["design_image_url"] = new_design.generated_image_path
        session.context = ctx
        db.commit()

        return json.dumps({
            "result": "Design refined successfully",
            "design_id": new_design.id,
            "version": new_design.version,
            "image_url": new_design.generated_image_path,
            "estimated_duration": new_design.estimated_duration,
            "difficulty_level": new_design.difficulty_level
        }, ensure_ascii=False)

    async def _tool_create_service_record(self, db, user_id, session,
                                          customer_id, design_plan_id=None,
                                          service_date=None):
        ctx = dict(session.context or {})
        effective_customer_id = customer_id or ctx.get("customer_id")
        effective_design_id = design_plan_id or ctx.get("design_plan_id")

        if not service_date:
            service_date = datetime.utcnow().date()
        elif isinstance(service_date, str):
            from datetime import date as _date
            service_date = _date.fromisoformat(service_date)

        service_data = {
            "customer_id": effective_customer_id,
            "design_plan_id": effective_design_id,
            "service_date": service_date,
            "status": "pending"
        }
        service = ServiceRecordService.create_service(db, service_data, user_id)

        # 更新 session.context
        ctx["service_record_id"] = service.id
        ctx["customer_id"] = service.customer_id
        session.context = ctx
        db.commit()

        return json.dumps({
            "result": "Service record created successfully",
            "service_id": service.id,
            "customer_id": service.customer_id,
            "design_plan_id": service.design_plan_id,
            "service_date": str(service.service_date),
            "status": service.status
        }, ensure_ascii=False)

    async def _tool_complete_service(self, db, user_id, session, service_id,
                                     actual_image_path=None, service_duration=None,
                                     materials_used=None, artist_review=None,
                                     customer_feedback=None, customer_satisfaction=None):
        ctx = dict(session.context or {})
        effective_service_id = service_id or ctx.get("service_record_id")
        # 优先使用 session.context 中已上传的实拍图
        actual_image_path = actual_image_path or ctx.get("actual_image_path")
        if not actual_image_path:
            return json.dumps({"error": "No actual photo uploaded yet. Please upload the completed photo first."}, ensure_ascii=False)

        completion_data = {
            "actual_image_path": actual_image_path,
            "service_duration": service_duration,
            "materials_used": materials_used,
            "artist_review": artist_review,
            "customer_feedback": customer_feedback,
            "customer_satisfaction": customer_satisfaction,
        }
        service = ServiceRecordService.complete_service(
            db, effective_service_id, completion_data, user_id
        )

        # 更新 session.context
        ctx["actual_image_path"] = actual_image_path
        session.context = ctx
        db.commit()

        return json.dumps({
            "result": "Service record completed",
            "service_id": service.id,
            "status": service.status,
            "service_duration": service.service_duration,
            "completed_at": service.completed_at.isoformat() if service.completed_at else None
        }, ensure_ascii=False)

    async def _tool_run_analysis(self, db, user_id, session, service_id):
        from app.models.service_record import ServiceRecord
        ctx = dict(session.context or {})
        effective_service_id = service_id or ctx.get("service_record_id")

        comparison = await AnalysisService.analyze_service(db, effective_service_id)

        # 更新 session.context
        ctx["comparison_result_id"] = comparison.id
        session.context = ctx
        db.commit()

        # 从 service_record 的关联获取能力评分
        scores = {}
        service_record = db.query(ServiceRecord).filter(
            ServiceRecord.id == effective_service_id
        ).first()
        if service_record and service_record.ability_records:
            for record in service_record.ability_records:
                if record.dimension:
                    scores[record.dimension.name] = record.score

        return json.dumps({
            "result": "AI analysis complete",
            "comparison_id": comparison.id,
            "similarity_score": comparison.similarity_score,
            "scores": scores,
            "differences": comparison.differences,
            "suggestions": comparison.suggestions
        }, ensure_ascii=False)

    async def _tool_get_ability_summary(self, db, user_id, session):
        summary = AbilityService.get_ability_summary(db, user_id)
        return json.dumps({
            "result": "Ability summary retrieved successfully",
            "summary": summary
        }, ensure_ascii=False)

    async def _tool_list_inspirations(self, db, user_id, session,
                                      search=None, category=None):
        from sqlalchemy import or_
        query = db.query(InspirationImage).filter(
            InspirationImage.user_id == user_id
        )
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                InspirationImage.title.like(pattern)
            )
        if category:
            query = query.filter(
                InspirationImage.category == category
            )
        inspirations = query.limit(10).all()
        data = []
        for insp in inspirations:
            data.append({
                "id": insp.id,
                "title": insp.title or "",
                "image_path": insp.image_path,
            })
        return json.dumps({
            "result": "Inspiration library",
            "total": len(data),
            "inspirations": data
        }, ensure_ascii=False)
