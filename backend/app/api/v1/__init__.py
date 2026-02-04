from fastapi import APIRouter
from app.api.v1 import auth, users, health, services, uploads

api_router = APIRouter()

# 注册子路由
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
