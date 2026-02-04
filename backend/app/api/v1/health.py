from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "nail-api"
    }


@router.get("/db")
async def database_health():
    # TODO: 实现数据库健康检查
    return {
        "status": "healthy",
        "database": "connected"
    }
