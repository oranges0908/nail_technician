"""
AI Agent 工具注册表（Tool Registry）
将已有业务 Service 方法封装为 OpenAI Function Calling 格式的工具。
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
            "description": "按姓名或手机号搜索已有客户，返回匹配列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "姓名或手机号关键词"
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
            "description": "创建新客户档案",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "客户姓名"},
                    "phone": {"type": "string", "description": "手机号（11位）"},
                    "email": {"type": "string", "description": "邮箱（可选）"},
                    "notes": {"type": "string", "description": "备注（可选）"}
                },
                "required": ["name", "phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_detail",
            "description": "获取指定客户的详细信息（含档案）",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "客户ID"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_design",
            "description": "调用 AI 生成美甲设计图。耗时约 30-60 秒，调用前告知用户正在处理",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "设计描述，包括风格、颜色、图案等"
                    },
                    "customer_id": {
                        "type": "integer",
                        "description": "客户ID（可选，用于读取客户偏好）"
                    },
                    "reference_images": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "参考图路径列表（可选）"
                    },
                    "style_keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "风格关键词列表（可选）"
                    },
                    "design_target": {
                        "type": "string",
                        "enum": ["single", "5nails", "10nails"],
                        "description": "设计目标（默认 10nails）"
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
            "description": "对已有设计方案进行 AI 优化迭代，生成新版本",
            "parameters": {
                "type": "object",
                "properties": {
                    "design_id": {
                        "type": "integer",
                        "description": "要优化的设计方案ID"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "优化指令，如「换成更深的粉色」「去掉钻石装饰」"
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
            "description": "创建今日服务记录，关联客户和设计方案",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "客户ID"
                    },
                    "design_plan_id": {
                        "type": "integer",
                        "description": "设计方案ID（可选）"
                    },
                    "service_date": {
                        "type": "string",
                        "description": "服务日期，格式 YYYY-MM-DD（不填则为今天）"
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
            "description": "完成服务记录，上传实拍图，记录时长和复盘",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "integer",
                        "description": "服务记录ID"
                    },
                    "actual_image_path": {
                        "type": "string",
                        "description": "实拍图路径（已上传到服务器的路径）"
                    },
                    "service_duration": {
                        "type": "integer",
                        "description": "服务时长（分钟）"
                    },
                    "materials_used": {
                        "type": "string",
                        "description": "使用材料描述（可选）"
                    },
                    "artist_review": {
                        "type": "string",
                        "description": "美甲师复盘感想（可选）"
                    },
                    "customer_feedback": {
                        "type": "string",
                        "description": "客户反馈（可选）"
                    },
                    "customer_satisfaction": {
                        "type": "integer",
                        "description": "客户满意度 1-5（可选）"
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
            "description": "对已完成的服务记录运行 AI 对比分析（设计图 vs 实拍图），生成6维评分。耗时 20-40 秒",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "integer",
                        "description": "服务记录ID"
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
            "description": "获取美甲师的能力分析总结，包括强项和待提升维度",
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
            "description": "搜索灵感图库，返回可用的参考图列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "搜索关键词（标题/标签，可选）"
                    },
                    "category": {
                        "type": "string",
                        "description": "分类过滤（可选）"
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
    将工具调用路由到对应的已有 Service 方法。
    执行后如产生新业务 ID，更新 session.context 并持久化到 DB。
    """

    async def execute(
        self,
        tool_name: str,
        tool_args: dict,
        db: Session,
        user_id: int,
        session: ConversationSession
    ) -> str:
        """执行工具，返回 LLM 友好的中文 JSON 字符串"""
        handler = getattr(self, f"_tool_{tool_name}", None)
        if not handler:
            return json.dumps(
                {"error": f"未知工具: {tool_name}"},
                ensure_ascii=False
            )
        try:
            return await handler(
                db=db, user_id=user_id, session=session, **tool_args
            )
        except Exception as e:
            logger.error(f"工具执行失败 {tool_name}: {e}", exc_info=True)
            # 提取 HTTPException 的 detail 字段（比 str(e) 更易读）
            detail = getattr(e, "detail", None) or str(e)
            return json.dumps(
                {"error": f"工具执行失败: {detail}"},
                ensure_ascii=False
            )

    async def _tool_search_customer(self, db, user_id, session, query):
        customers, total = CustomerService.list_customers(
            db, user_id, search=query, limit=5
        )
        if total == 0:
            return json.dumps(
                {"result": "未找到匹配客户", "total": 0, "customers": []},
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
        return json.dumps(
            {"result": "找到以下客户", "total": total, "customers": data},
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
            "result": "客户创建成功",
            "customer_id": customer.id,
            "name": customer.name,
            "phone": customer.phone
        }, ensure_ascii=False)

    async def _tool_get_customer_detail(self, db, user_id, session, customer_id):
        customer = CustomerService.get_customer_by_id(db, customer_id, user_id)
        if not customer:
            return json.dumps(
                {"error": f"客户 ID {customer_id} 不存在"},
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
            "result": "设计图生成成功",
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
            "result": "设计图优化成功",
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
        session.context = ctx
        db.commit()

        return json.dumps({
            "result": "服务记录创建成功",
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
            return json.dumps({"error": "尚未上传实拍图，请先上传实拍完成图"}, ensure_ascii=False)

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
            "result": "服务记录已完成",
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
            "result": "AI 分析完成",
            "comparison_id": comparison.id,
            "similarity_score": comparison.similarity_score,
            "scores": scores,
            "differences": comparison.differences,
            "suggestions": comparison.suggestions
        }, ensure_ascii=False)

    async def _tool_get_ability_summary(self, db, user_id, session):
        summary = AbilityService.get_ability_summary(db, user_id)
        return json.dumps({
            "result": "能力总结获取成功",
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
            "result": "灵感图库",
            "total": len(data),
            "inspirations": data
        }, ensure_ascii=False)
