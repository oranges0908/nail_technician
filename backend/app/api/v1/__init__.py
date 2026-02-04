from fastapi import APIRouter
from app.api.v1 import auth, users, health

api_router = APIRouter()

# 注册子路由
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
