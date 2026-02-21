"""
AI Agent 对话服务（核心）
- 管理会话生命周期
- 多轮 LLM 推理 + Function Calling 执行
- 步骤完成后压缩历史（滚动摘要）
- 协调 DB（元数据）和本地文件（原始消息）双写
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

# 步骤流转顺序（用于自动推进）
STEP_FLOW = ["greeting", "customer", "design", "service", "complete", "analysis", "review"]

# 系统基础提示词模板
_BASE_SYSTEM_PROMPT = """你是一个专业美甲师 AI 助理，通过自然对话帮助美甲师完成完整服务流程。
语言：中文，风格亲切简洁。

{summaries_section}当前上下文：
{context_section}

【工具调用阶段】需要查询或执行操作时，直接发出 tool call，不要同时输出任何文字：

搜索类工具（search_customer, list_inspirations, get_customer_detail, get_ability_summary）：
- 用户提供客户姓名/手机号时，立即发出 search_customer tool call，不要先输出任何文字

创建/生成类工具（create_customer, generate_design, create_service_record 等）分两轮处理：
- 第一轮（收到用户需求）：输出 JSON 告知操作内容，请用户确认；quick_replies 必须含 ["是", "否", "其他问题"]
- 第二轮（用户回复"是"确认）：**立即发出 tool call**，不要再输出"正在创建/生成"等文字；等待工具返回后再输出最终 JSON

generate_design 工具返回成功后，最终 JSON 中设 ui_hint="show_design_preview"，ui_data 填入 design_id 和 image_url

- 向用户提出是/否类问题时，quick_replies 必须包含 ["是", "否", "其他问题"]
- 每步完成、用户确认满意后，将 step_complete 设为 true

【最终回复阶段】所有工具调用完成后，必须以合法 JSON 格式输出一次且仅一次最终回复（不含任何额外文字）：
{{
  "message_text": "面向用户的中文消息",
  "step_summary": "本步骤关键信息摘要（20-50字）",
  "step_complete": false,
  "quick_replies": ["选项1", "选项2"],
  "ui_hint": "none|show_customer_card|show_design_preview|show_upload_button|show_analysis_result|show_final_summary",
  "ui_data": null,
  "needs_image_upload": false
}}"""

# 开场问候消息
_OPENING_MESSAGE_TEXT = (
    "你好！我是你的 AI 美甲助理 ✨\n\n"
    "我可以帮你完成整个服务流程：\n"
    "① 查找或新建客户\n"
    "② AI 生成设计方案\n"
    "③ 创建服务记录\n"
    "④ 上传实拍 + 完成服务\n"
    "⑤ AI 对比分析\n"
    "⑥ 成长复盘总结\n\n"
    "请问今天要服务哪位客户？"
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
        """创建会话，生成本地文件，写入开场问候，返回 (会话, 开场消息)"""
        session = ConversationSession(
            user_id=user_id,
            status="active",
            current_step="greeting",
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
            "step": "greeting",
            "archived": False,
            "role": "assistant",
            "content": _OPENING_MESSAGE_TEXT,
        })

        opening_msg = AssistantMessageResponse(
            content=_OPENING_MESSAGE_TEXT,
            ui_metadata=UiMetadata(
                quick_replies=["查找老客户", "新建客户档案", "直接生成设计"],
                ui_hint="none",
                ui_data=None,
                needs_image_upload=False,
            ),
            step_complete=False,
            current_step="greeting",
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
            raise ValueError(f"会话 {session_id} 不存在")
        if session.status != "active":
            raise ValueError(f"会话 {session_id} 已结束（状态: {session.status}）")

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
            user_msg_content += f"\n[已附带图片: {', '.join(image_paths)}]"

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
                # 没有工具调用 → 这是最终回复
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
                    tool_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    tool_args = {}

                logger.info(f"执行工具: {tool_name}，参数: {tool_args}")
                tool_result = await self._tools.execute(
                    tool_name, tool_args, db, user_id, session
                )
                logger.info(f"工具结果: {tool_result[:200]}")

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
            raise ValueError(f"会话 {session_id} 不存在")

        ctx = dict(session.context or {})
        if purpose == "inspiration":
            paths = list(ctx.get("inspiration_paths", []))
            paths.append(saved_path)
            ctx["inspiration_paths"] = paths
        elif purpose == "actual":
            ctx["actual_image_path"] = saved_path

        session.context = ctx
        db.commit()

        # 写入系统提示消息，告知 LLM 图片已上传
        system_notice = {
            "step": session.current_step,
            "archived": False,
            "role": "system",
            "content": f"[用户上传了 {purpose} 图片，路径: {saved_path}]",
        }
        self._file_mgr.append_message(session_id, system_notice)

        # 触发 LLM 响应
        upload_msg = (
            f"我上传了一张{'参考灵感图' if purpose == 'inspiration' else '实拍完成图'}。"
        )
        return await self.process_message(
            db, session_id, user_id, upload_msg, image_paths=[saved_path]
        )

    # ── 私有：LLM 调用 ────────────────────────────────────────────────────

    async def _call_llm(
        self, openai_messages: List[dict], with_tools: bool = True
    ) -> dict:
        """调用 OpenAI Chat Completions API，返回 message 字典"""
        kwargs = {
            "model": self._model,
            "messages": openai_messages,
            "temperature": 0.7,
        }
        if with_tools:
            kwargs["tools"] = TOOLS_DEFINITION
            kwargs["tool_choice"] = "auto"

        response = await self._llm.chat.completions.create(**kwargs)
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
            summaries_section = f"已完成步骤摘要（这是你了解当前进度的依据）：\n{lines}\n\n"
        else:
            summaries_section = ""

        # 构建上下文描述
        context_parts = []
        if ctx.get("customer_id"):
            context_parts.append(
                f"客户: {ctx.get('customer_name', '')} (ID: {ctx['customer_id']})"
            )
        if ctx.get("design_plan_id"):
            context_parts.append(f"设计方案 ID: {ctx['design_plan_id']}")
        if ctx.get("service_record_id"):
            context_parts.append(f"服务记录 ID: {ctx['service_record_id']}")
        if ctx.get("comparison_result_id"):
            context_parts.append(f"分析结果 ID: {ctx['comparison_result_id']}")
        if ctx.get("actual_image_path"):
            context_parts.append(f"实拍图: {ctx['actual_image_path']}")

        context_section = (
            "\n".join(context_parts) if context_parts else "（暂无业务数据）"
        )

        return _BASE_SYSTEM_PROMPT.format(
            summaries_section=summaries_section,
            context_section=context_section,
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
                message_text="好的，请继续。",
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
            # 降级：直接将 content 作为纯文本消息
            logger.warning(f"LLM 响应不是合法 JSON，降级处理: {content[:100]}")
            return LLMResponse(
                message_text=content,
                step_summary="",
                step_complete=False,
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
