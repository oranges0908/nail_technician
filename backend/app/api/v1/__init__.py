from fastapi import APIRouter
from app.api.v1 import auth, users, health, system, services, uploads, customers, inspirations, designs, abilities

api_router = APIRouter()

# 注册子路由
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(services.router, prefix="/services", tags=["Services"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["File Upload"])
api_router.include_router(inspirations.router, prefix="/inspirations", tags=["Inspirations"])
api_router.include_router(designs.router, prefix="/designs", tags=["Design Plans"])
api_router.include_router(abilities.router, prefix="/abilities", tags=["Abilities"])
