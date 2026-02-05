"""
健康检查端点

提供系统健康状态检查，包括数据库连接状态。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get(
    "",
    summary="基础健康检查",
    description="返回API服务的基本健康状态",
    response_description="健康状态信息",
    tags=["Health"]
)
async def health_check() -> Dict[str, Any]:
    """
    基础健康检查端点

    Returns:
        - status: 服务状态（healthy/unhealthy）
        - timestamp: 当前时间戳（UTC）
        - service: 服务名称
        - version: API版本
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get(
    "/detailed",
    summary="详细健康检查",
    description="检查数据库连接状态和系统详细信息",
    response_description="详细的系统健康状态",
    tags=["Health"]
)
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    详细健康检查端点

    检查项：
    - 数据库连接状态
    - 数据库响应时间

    Returns:
        - status: 整体状态
        - timestamp: 检查时间
        - database: 数据库状态详情
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # 检查数据库连接
    try:
        start_time = datetime.utcnow()
        db.execute(text("SELECT 1"))
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000  # 毫秒

        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "type": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    return health_status
