"""
系统信息端点

提供系统版本、环境配置等信息。
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any
import platform
import sys

from app.core.config import settings

router = APIRouter()


@router.get(
    "/info",
    summary="系统信息",
    description="获取系统版本、环境、运行时信息",
    response_description="系统详细信息",
    tags=["System"]
)
async def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息

    Returns:
        - app: 应用信息（名称、版本）
        - environment: 运行环境
        - python: Python版本
        - platform: 平台信息
        - api_prefix: API路径前缀
        - docs_url: API文档URL
    """
    return {
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG
        },
        "environment": {
            "host": settings.HOST,
            "port": settings.PORT,
            "database": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
            "log_level": settings.LOG_LEVEL
        },
        "runtime": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.machine()
        },
        "api": {
            "prefix": settings.API_V1_PREFIX,
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/version",
    summary="API版本",
    description="获取API版本号",
    response_description="版本信息",
    tags=["System"]
)
async def get_version() -> Dict[str, str]:
    """
    获取API版本信息

    Returns:
        - version: API版本号
        - name: 应用名称
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
