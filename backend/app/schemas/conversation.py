"""
AI 对话助理 — API 契约 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ── UI 元数据 ───────────────────────────────────────────────────────────────

class UiMetadata(BaseModel):
    """返回给前端的 UI 渲染提示"""
    quick_replies: List[str] = []
    # none | show_customer_card | show_design_preview | show_upload_button
    # | show_analysis_result | show_final_summary
    ui_hint: str = "none"
    ui_data: Optional[Dict[str, Any]] = None
    needs_image_upload: bool = False


# ── LLM 内部解析格式 ────────────────────────────────────────────────────────

class LLMResponse(BaseModel):
    """LLM 输出的结构化格式（内部解析用，不暴露给前端）"""
    message_text: str
    step_summary: str = ""
    step_complete: bool = False
    quick_replies: List[str] = []
    ui_hint: str = "none"
    ui_data: Optional[Dict[str, Any]] = None
    needs_image_upload: bool = False


# ── 请求 Schema ─────────────────────────────────────────────────────────────

class ConversationMessageCreate(BaseModel):
    """用户发送消息请求体"""
    content: str = Field(..., min_length=1, max_length=5000)
    image_paths: List[str] = []


# ── 响应 Schema ─────────────────────────────────────────────────────────────

class AssistantMessageResponse(BaseModel):
    """返回给前端的助理消息"""
    content: str
    ui_metadata: UiMetadata
    step_complete: bool
    current_step: str
    context: Dict[str, Any]


class ConversationSessionResponse(BaseModel):
    """会话摘要响应（列表页使用）"""
    id: int
    user_id: int
    status: str
    current_step: str
    context: Dict[str, Any]
    step_summaries: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StartSessionResponse(BaseModel):
    """创建会话响应（含开场问候消息）"""
    session_id: int
    status: str
    current_step: str
    context: Dict[str, Any]
    opening_message: AssistantMessageResponse
    created_at: datetime


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    message: AssistantMessageResponse
    session_id: int


class SessionListResponse(BaseModel):
    """会话列表响应"""
    total: int
    sessions: List[ConversationSessionResponse]
