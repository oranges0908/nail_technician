"""
AI 对话助理 API
"""
import logging
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationMessageCreate,
    ConversationSessionResponse,
    SendMessageResponse,
    SessionListResponse,
    StartSessionResponse,
)
from app.services.agent_service import AgentService
from app.api.v1.uploads import save_upload_file, validate_file

logger = logging.getLogger(__name__)

router = APIRouter()

# 单例 AgentService（包含 OpenAI 客户端，复用）
_agent_service = AgentService()


# ── 会话管理 ──────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建 AI 对话会话",
    description="新建一个 AI 对话会话，返回会话 ID 和开场问候消息"
)
async def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    session, opening_msg = _agent_service.create_session(db, current_user.id)
    return StartSessionResponse(
        session_id=session.id,
        status=session.status,
        current_step=session.current_step,
        context=session.context or {},
        opening_message=opening_msg,
        created_at=session.created_at,
    )


@router.get(
    "",
    response_model=SessionListResponse,
    summary="列出历史会话",
    description="分页获取当前用户的所有对话会话（按创建时间倒序）"
)
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sessions, total = AgentService.list_sessions(db, current_user.id, skip, limit)
    return SessionListResponse(total=total, sessions=sessions)


@router.get(
    "/{session_id}",
    response_model=ConversationSessionResponse,
    summary="获取会话详情",
    description="获取指定会话的元数据（步骤摘要、当前上下文等）"
)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    session = AgentService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_id} 不存在"
        )
    return session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="放弃会话",
    description="将会话状态标记为 abandoned"
)
async def abandon_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ok = AgentService.abandon_session(db, session_id, current_user.id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_id} 不存在"
        )


# ── 消息交互 ──────────────────────────────────────────────────────────────

@router.post(
    "/{session_id}/messages",
    response_model=SendMessageResponse,
    summary="发送消息",
    description="向 AI 助理发送消息，返回助理回复（含 UI 元数据和步骤信息）"
)
async def send_message(
    session_id: int,
    body: ConversationMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        reply = await _agent_service.process_message(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            content=body.content,
            image_paths=body.image_paths or [],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Agent 处理消息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 助理处理失败: {str(e)}"
        )
    return SendMessageResponse(message=reply, session_id=session_id)


@router.post(
    "/{session_id}/images",
    response_model=SendMessageResponse,
    summary="会话内图片上传",
    description="在对话中上传图片（灵感图或实拍图），返回助理回复"
)
async def upload_image_in_session(
    session_id: int,
    file: UploadFile = File(...),
    purpose: Optional[str] = Query(
        "inspiration",
        description="图片用途: inspiration（灵感图）或 actual（实拍图）"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 验证会话存在
    session = AgentService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_id} 不存在"
        )

    # 验证 purpose
    if purpose not in ("inspiration", "actual"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="purpose 只能是 inspiration 或 actual"
        )

    # 保存图片到对应目录（复用现有上传逻辑）
    category = "inspirations" if purpose == "inspiration" else "actuals"
    try:
        upload_result = await save_upload_file(file, category, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片保存失败: {str(e)}"
        )

    # 触发 Agent 处理（更新上下文 + LLM 响应）
    try:
        reply = await _agent_service.handle_image_upload(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            saved_path=upload_result.file_url,
            purpose=purpose,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Agent 处理图片上传失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 助理处理图片失败: {str(e)}"
        )

    return SendMessageResponse(message=reply, session_id=session_id)
