"""
AI Agent conversation service (core)
- Manages session lifecycle
- Multi-turn LLM reasoning + Function Calling execution
- Compress history after step completion (rolling summary)
- Coordinate DB (metadata) and local file (raw messages) dual-write
"""
import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
import datetime

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.conversation_session import ConversationSession
from app.schemas.conversation import (
    LLMResponse,
    UiMetadata,
    AssistantMessageResponse,
)
from app.services.conversation_file import ConversationFileManager
from app.services.agent_tools import TOOLS_DEFINITION, ToolExecutor

logger = logging.getLogger(__name__)

# Step flow order (for auto-advancement)
STEP_FLOW = ["collect", "confirm", "analysis", "review"]

# Base system prompt template
_BASE_SYSTEM_PROMPT = """You are a professional nail artist AI assistant, helping nail artists complete service records and reviews through natural conversation. Language: English, concise and friendly.

{summaries_section}Current context:
{context_section}

{step_instructions}

[Final response format] After all tool calls are complete, output only valid JSON (no other text):
{{
  "message_text": "User-facing English message",
  "step_summary": "Step summary (use full JSON string in collect phase)",
  "step_complete": false,
  "quick_replies": [],
  "ui_hint": "none|show_customer_card|show_design_preview|show_upload_button|show_analysis_result|show_final_summary",
  "ui_data": null,
  "needs_image_upload": false
}}"""

# Step-specific instructions
_STEP_INSTRUCTIONS = {
    "collect": """[collect step — free-form service description collection]
The user can describe today's service in natural language without following any order. Multiple messages to add information are allowed.
- Optionally call search_customer (for information lookup only, do not write any records)
- NEVER call create_service_record or complete_service in this step
- If user uploads an image, record has_actual_image=true
- When user says "that's all" / "done" / "write it" or the input contains complete service information, trigger step_complete=true

When triggering completion, output a structured draft in message_text for user preview, and set step_summary to the following complete JSON string:
{
  "customer_name": "customer name (leave empty if not mentioned)",
  "estimated_duration": null,
  "actual_duration": 240,
  "materials": "gel polish + top coat",
  "design_desc": "reference design description",
  "actual_desc": "description of actual completed result",
  "reflection": "nail artist's review thoughts",
  "customer_feedback": "customer feedback",
  "style_tags": ["style tag 1"],
  "customer_satisfaction": 5,
  "has_actual_image": false,
  "pending_fields": ["list of missing fields"]
}""",

    "confirm": """[confirm step — confirm and write record]
Read the structured data (JSON string) from the collect step in step_summaries.
- If there are pending_fields, ask at most 2 missing fields at once, do not ask repeatedly
- After receiving user confirmation ("confirm" / "yes" / "write"), call tools in order:
  1. search_customer(customer_name) → if exactly 1 result, use automatically; if 0 results, call create_customer; if multiple, show options for user to choose
  2. create_service_record(customer_id, design_plan_id=None)
  3. complete_service(service_id, actual_image_path, service_duration, materials_used, artist_review, customer_feedback, customer_satisfaction)
- Set step_complete=true after all writes are complete
- quick_replies should include ["Confirm & Save", "Edit Details"]""",

    "analysis": """[analysis step — AI analysis]
- If service_record_id exists in context: call run_analysis(service_id)
- Show analysis highlights (up to 3 strengths + 3 areas to improve), set step_complete=true
- If no service_record_id or analysis fails: set step_complete=true directly to skip""",

    "review": """[review step — growth review]
- Call get_ability_summary() to get ability summary
- Output 1-3 personalized growth suggestions, set step_complete=true""",
}

# Opening greeting message
_OPENING_MESSAGE_TEXT = (
    "Hi! I'm your AI nail assistant ✨\n\n"
    "Just chat with me naturally about today's service.\n"
    "For example: \"Today I did a green-gold totem design for Momo, referenced the design plan, the result turned out great, took 4 hours, but the top coat wasn't leveled well...\"\n\n"
    "When you're done, just say \"that's all\" and I'll organize a draft for you to confirm before saving the record 📝\n"
    "You can also upload the actual photo or reference images 📷"
)


class AgentService:
    """AI Agent 对话服务"""

    def __init__(self):
        self._tools = ToolExecutor()
        self._file_mgr = ConversationFileManager()
        if settings.AI_PROVIDER == "gemini":
            self._llm = AsyncOpenAI(
                api_key=settings.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            self._model = "gemini-2.0-flash"
        else:
            self._llm = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._model = "gpt-4o"

    # ── 会话管理 ──────────────────────────────────────────────────────────

    def create_session(
        self, db: Session, user_id: int
    ) -> Tuple[ConversationSession, AssistantMessageResponse]:
        """Create session, generate local file, write opening greeting, return (session, opening message)"""
        session = ConversationSession(
            user_id=user_id,
            status="active",
            current_step="collect",
            context={},
            step_summaries=[],
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 设置文件路径
        file_path = str(self._file_mgr.get_file_path(session.id))
        session.file_path = file_path
        db.commit()

        # 写入开场问候到本地文件
        self._file_mgr.append_message(session.id, {
            "step": "collect",
            "archived": False,
            "role": "assistant",
            "content": _OPENING_MESSAGE_TEXT,
        })

        opening_msg = AssistantMessageResponse(
            content=_OPENING_MESSAGE_TEXT,
            ui_metadata=UiMetadata(
                quick_replies=[],
                ui_hint="none",
                ui_data=None,
                needs_image_upload=False,
            ),
            step_complete=False,
            current_step="collect",
            context={},
        )
        return session, opening_msg

    @staticmethod
    def get_session(
        db: Session, session_id: int, user_id: int
    ) -> Optional[ConversationSession]:
        return db.query(ConversationSession).filter(
            ConversationSession.id == session_id,
            ConversationSession.user_id == user_id
        ).first()

    @staticmethod
    def list_sessions(
        db: Session, user_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ConversationSession], int]:
        query = db.query(ConversationSession).filter(
            ConversationSession.user_id == user_id
        )
        total = query.count()
        sessions = query.order_by(
            ConversationSession.created_at.desc()
        ).offset(skip).limit(limit).all()
        return sessions, total

    @staticmethod
    def abandon_session(
        db: Session, session_id: int, user_id: int
    ) -> bool:
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_id,
            ConversationSession.user_id == user_id
        ).first()
        if not session:
            return False
        session.status = "abandoned"
        session.updated_at = datetime.datetime.utcnow()
        db.commit()
        return True

    # ── 核心：处理用户消息 ────────────────────────────────────────────────

    async def process_message(
        self,
        db: Session,
        session_id: int,
        user_id: int,
        content: str,
        image_paths: Optional[List[str]] = None,
    ) -> AssistantMessageResponse:
        """
        Agent 推理循环：
        1. 加载会话（DB）+ 当前步骤消息（本地文件）
        2. 构建 OpenAI messages（system + current_step_messages）
        3. 追加用户消息并写入文件
        4. 调用 LLM，循环处理 tool_calls（最多 8 轮）
        5. 解析最终 JSON 响应
        6. 步骤完成时执行归档 + 摘要持久化
        7. 返回 AssistantMessageResponse
        """
        # 1. 加载会话
        session = self.get_session(db, session_id, user_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        if session.status != "active":
            raise ValueError(f"Session {session_id} has ended (status: {session.status})")

        # User manually terminates session
        if content.strip() in ("终止", "abort", "quit"):
            self.abandon_session(db, session_id, user_id)
            return AssistantMessageResponse(
                content="Session has been terminated. Start a new session to begin a new service.",
                ui_metadata=UiMetadata(
                    quick_replies=[],
                    ui_hint="none",
                    ui_data=None,
                    needs_image_upload=False,
                ),
                step_complete=False,
                current_step="done",
                context={},
            )

        current_step = session.current_step

        # 2. 读取当前步骤历史消息（本地文件）
        step_messages = self._file_mgr.read_current_step_messages(
            session_id, current_step
        )

        # 3. 构建 OpenAI messages
        system_prompt = self._build_system_prompt(session)
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages += self._build_openai_messages(step_messages)

        # 4. 追加用户消息
        user_msg_content = content
        if image_paths:
            user_msg_content += f"\n[Image attached: {', '.join(image_paths)}]"

        user_msg = {
            "step": current_step,
            "archived": False,
            "role": "user",
            "content": user_msg_content,
        }
        self._file_mgr.append_message(session_id, user_msg)
        openai_messages.append({"role": "user", "content": user_msg_content})

        # 5. LLM 推理循环（最多 8 轮，处理 tool_calls）
        # 记录推理前的设计 ID，用于事后检测是否新生成了设计
        _pre_design_id = (session.context or {}).get("design_plan_id")

        max_rounds = 8
        for round_idx in range(max_rounds):
            response = await self._call_llm(openai_messages, with_tools=True)

            # 检查是否有 tool_calls
            tool_calls = response.get("tool_calls")
            if not tool_calls:
                content_text = response.get("content") or ""
                # 检测 LLM 用口语"替代"了工具调用（首轮、未生成设计时）
                _intent_keywords = ("generating", "creating", "working on",
                                    "just a moment", "please wait", "I'll generate", "I will generate")
                _needs_tool = (
                    round_idx == 0
                    and not (session.context or {}).get("design_plan_id")
                    and any(kw in content_text for kw in _intent_keywords)
                )
                if _needs_tool:
                    logger.warning(
                        f"[session={session_id}] LLM used text instead of tool call, forcing retry: {content_text[:80]!r}"
                    )
                    openai_messages.append({"role": "assistant", "content": content_text})
                    openai_messages.append({
                        "role": "user",
                        "content": "Please call the tool immediately. Do not output any text.",
                    })
                    response = await self._call_llm(openai_messages, with_tools=True, force_tool=True)
                    tool_calls = response.get("tool_calls")
                    if not tool_calls:
                        logger.error(f"[session={session_id}] Still no tool call after forced retry, giving up")
                        break
                else:
                    if round_idx == 0:
                        logger.warning(
                            f"[session={session_id}] LLM did not issue tool call on first round, returning text directly: {content_text[:80]!r}"
                        )
                    break

            # a. 将带 tool_calls 的 assistant 消息追加
            assistant_with_tools = {
                "step": current_step,
                "archived": False,
                "role": "assistant",
                "tool_calls": tool_calls,
            }
            self._file_mgr.append_message(session_id, assistant_with_tools)
            openai_messages.append({
                "role": "assistant",
                "content": response.get("content"),  # 必须原样传回，即使为 None
                "tool_calls": tool_calls,
            })

            # b. 执行每个 tool，追加 tool result
            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    tool_args = json.loads(tc["function"]["arguments"] or "{}")
                except (json.JSONDecodeError, TypeError):
                    tool_args = {}

                logger.info(f"Executing tool: {tool_name}, args: {tool_args}")
                tool_result = await self._tools.execute(
                    tool_name, tool_args, db, user_id, session
                )
                logger.info(f"Tool result: {tool_result[:200]}")

                tool_result_msg = {
                    "step": current_step,
                    "archived": False,
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tool_name,
                    "content": tool_result,
                }
                self._file_mgr.append_message(session_id, tool_result_msg)
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tool_name,
                    "content": tool_result,
                })

        # 6. 解析最终文本回复
        final_content = response.get("content") or ""
        llm_resp = self._parse_llm_response(final_content)

        # 6a. 若本轮工具调用生成了新设计，强制设置 show_design_preview（不依赖 LLM 输出）
        _post_ctx = session.context or {}
        _new_design_id = _post_ctx.get("design_plan_id")
        _new_design_url = _post_ctx.get("design_image_url")
        if _new_design_id and _new_design_id != _pre_design_id and _new_design_url:
            llm_resp = LLMResponse(
                message_text=llm_resp.message_text,
                step_summary=llm_resp.step_summary,
                step_complete=llm_resp.step_complete,
                quick_replies=llm_resp.quick_replies,
                ui_hint="show_design_preview",
                ui_data={
                    "design_id": _new_design_id,
                    "image_url": _new_design_url,
                    "style_keywords": llm_resp.ui_data.get("style_keywords", [])
                    if isinstance(llm_resp.ui_data, dict) else [],
                },
                needs_image_upload=llm_resp.needs_image_upload,
            )

        # 6b. 实拍图已存在时，强制清除 needs_image_upload（防止 LLM 重复要求上传）
        if _post_ctx.get("actual_image_path") and llm_resp.needs_image_upload:
            logger.warning(
                f"[session={session_id}] Actual image already exists but LLM still outputs needs_image_upload=true, forcing to false"
            )
            llm_resp = LLMResponse(
                message_text=llm_resp.message_text,
                step_summary=llm_resp.step_summary,
                step_complete=llm_resp.step_complete,
                quick_replies=llm_resp.quick_replies,
                ui_hint=llm_resp.ui_hint,
                ui_data=llm_resp.ui_data,
                needs_image_upload=False,
            )

        # 7. 将助理最终消息写入本地文件
        assistant_final = {
            "step": current_step,
            "archived": False,
            "role": "assistant",
            "content": llm_resp.message_text,
            "ui_metadata": {
                "quick_replies": llm_resp.quick_replies,
                "ui_hint": llm_resp.ui_hint,
                "ui_data": llm_resp.ui_data,
                "needs_image_upload": llm_resp.needs_image_upload,
            },
        }
        self._file_mgr.append_message(session_id, assistant_final)

        # 8. 更新 DB 中的步骤摘要（每次都更新最新摘要）
        summaries = list(session.step_summaries or [])
        # 替换或追加当前步骤摘要
        step_entry = {"step": current_step, "summary": llm_resp.step_summary}
        existing_idx = next(
            (i for i, s in enumerate(summaries) if s.get("step") == current_step),
            None
        )
        if existing_idx is not None:
            summaries[existing_idx] = step_entry
        else:
            summaries.append(step_entry)
        session.step_summaries = summaries
        session.updated_at = datetime.datetime.utcnow()

        # 9. 步骤完成处理
        if llm_resp.step_complete:
            # 归档当前步骤消息（本地文件）
            self._file_mgr.archive_step(session_id, current_step)

            # 推进到下一步
            next_step = self._next_step(current_step)
            session.current_step = next_step

            if next_step == "done":
                session.status = "completed"
                session.completed_at = datetime.datetime.utcnow()

        db.commit()

        return AssistantMessageResponse(
            content=llm_resp.message_text,
            ui_metadata=UiMetadata(
                quick_replies=llm_resp.quick_replies,
                ui_hint=llm_resp.ui_hint,
                ui_data=llm_resp.ui_data,
                needs_image_upload=llm_resp.needs_image_upload,
            ),
            step_complete=llm_resp.step_complete,
            current_step=session.current_step,
            context=dict(session.context or {}),
        )

    async def handle_image_upload(
        self,
        db: Session,
        session_id: int,
        user_id: int,
        saved_path: str,
        purpose: str,
    ) -> AssistantMessageResponse:
        """
        处理图片上传：
        1. 更新 session.context（inspiration_paths 或 actual_image_path）
        2. 写入 system 说明消息到本地文件
        3. 触发 process_message 获取 LLM 响应
        """
        session = self.get_session(db, session_id, user_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        ctx = dict(session.context or {})
        if purpose == "inspiration":
            paths = list(ctx.get("inspiration_paths", []))
            paths.append(saved_path)
            ctx["inspiration_paths"] = paths
        elif purpose == "actual":
            ctx["actual_image_path"] = saved_path

        session.context = ctx
        db.commit()

        # Write system notice to tell LLM that image was uploaded
        system_notice = {
            "step": session.current_step,
            "archived": False,
            "role": "system",
            "content": f"[User uploaded a {purpose} image, path: {saved_path}]",
        }
        self._file_mgr.append_message(session_id, system_notice)

        # Trigger LLM response
        upload_msg = (
            f"I uploaded a {'reference/inspiration image' if purpose == 'inspiration' else 'actual completed photo'}."
        )
        return await self.process_message(
            db, session_id, user_id, upload_msg, image_paths=[saved_path]
        )

    # ── 私有：LLM 调用 ────────────────────────────────────────────────────

    async def _call_llm(
        self, openai_messages: List[dict], with_tools: bool = True,
        force_tool: bool = False
    ) -> dict:
        """调用 OpenAI Chat Completions API，返回 message 字典"""
        kwargs = {
            "model": self._model,
            "messages": openai_messages,
            "temperature": 0.7,
        }
        if with_tools:
            kwargs["tools"] = TOOLS_DEFINITION
            kwargs["tool_choice"] = "required" if force_tool else "auto"

        logger.info(
            "[LLM input] model=%s messages=%s",
            kwargs["model"],
            json.dumps(openai_messages, ensure_ascii=False),
        )
        response = await self._llm.chat.completions.create(**kwargs)
        if not response.choices:
            logger.warning("LLM returned empty choices, treating as empty response")
            return {"content": None}
        msg = response.choices[0].message

        result = {"content": msg.content}
        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in msg.tool_calls
            ]
        return result

    def _build_system_prompt(self, session: ConversationSession) -> str:
        """构建系统提示词：基础提示 + 历史步骤摘要"""
        summaries = session.step_summaries or []
        ctx = session.context or {}

        if summaries:
            lines = "\n".join(
                f"- {s.get('step', '')}: {s.get('summary', '')}"
                for s in summaries
            )
            summaries_section = f"Completed step summaries (your reference for current progress):\n{lines}\n\n"
        else:
            summaries_section = ""

        # Build context description
        context_parts = []
        if ctx.get("customer_id"):
            context_parts.append(
                f"Customer: {ctx.get('customer_name', '')} (ID: {ctx['customer_id']})"
            )
        if ctx.get("design_plan_id"):
            context_parts.append(f"Design Plan ID: {ctx['design_plan_id']}")
        if ctx.get("service_record_id"):
            context_parts.append(f"Service Record ID: {ctx['service_record_id']}")
        if ctx.get("comparison_result_id"):
            context_parts.append(f"Analysis Result ID: {ctx['comparison_result_id']}")
        if ctx.get("actual_image_path"):
            context_parts.append(f"Actual photo: {ctx['actual_image_path']}")

        context_section = (
            "\n".join(context_parts) if context_parts else "(no business data yet)"
        )

        step_instructions = _STEP_INSTRUCTIONS.get(session.current_step, "")
        return _BASE_SYSTEM_PROMPT.format(
            summaries_section=summaries_section,
            context_section=context_section,
            step_instructions=step_instructions,
        )

    def _build_openai_messages(self, step_messages: List[dict]) -> List[dict]:
        """将本地文件格式的消息转换为 OpenAI API 格式"""
        result = []
        for msg in step_messages:
            role = msg.get("role")
            if role == "user":
                result.append({"role": "user", "content": msg.get("content", "")})
            elif role == "assistant":
                if msg.get("tool_calls"):
                    result.append({
                        "role": "assistant",
                        "tool_calls": msg["tool_calls"]
                    })
                else:
                    result.append({
                        "role": "assistant",
                        "content": msg.get("content", "")
                    })
            elif role == "tool":
                result.append({
                    "role": "tool",
                    "tool_call_id": msg.get("tool_call_id", ""),
                    "name": msg.get("name", ""),
                    "content": msg.get("content", "")
                })
            elif role == "system":
                result.append({
                    "role": "system",
                    "content": msg.get("content", "")
                })
        return result

    def _parse_llm_response(self, content: str) -> LLMResponse:
        """
        解析 LLM 输出的 JSON，容错处理。
        LLM 偶尔会用 markdown 代码块包裹 JSON，或输出纯文本。
        """
        if not content:
            return LLMResponse(
                message_text="Got it, please continue.",
                step_summary="",
                step_complete=False,
            )

        # 尝试从 markdown 代码块提取
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        # 尝试提取最外层 JSON 对象
        brace_match = re.search(r"\{.*\}", content, re.DOTALL)
        if brace_match:
            content = brace_match.group(0)

        try:
            data = json.loads(content)
            return LLMResponse(
                message_text=data.get("message_text", content),
                step_summary=data.get("step_summary", ""),
                step_complete=bool(data.get("step_complete", False)),
                quick_replies=data.get("quick_replies", []),
                ui_hint=data.get("ui_hint", "none"),
                ui_data=data.get("ui_data"),
                needs_image_upload=bool(data.get("needs_image_upload", False)),
            )
        except (json.JSONDecodeError, Exception):
            # Fallback: use content as plain text message and provide retry/abort options
            logger.warning(f"LLM response is not valid JSON, falling back: {content[:100]}")
            return LLMResponse(
                message_text=content,
                step_summary="",
                step_complete=False,
                quick_replies=["Retry", "Abort"],
            )

    @staticmethod
    def _next_step(current_step: str) -> str:
        """返回下一个步骤名称"""
        try:
            idx = STEP_FLOW.index(current_step)
            if idx + 1 < len(STEP_FLOW):
                return STEP_FLOW[idx + 1]
        except ValueError:
            pass
        return "done"
