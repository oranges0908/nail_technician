from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.exceptions import NailAppException
from app.core.limiter import limiter
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.v1 import api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os
import logging

# 配置日志
setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

# API标签元数据（用于Swagger UI文档分组）
tags_metadata = [
    {
        "name": "Health",
        "description": "健康检查端点。用于监控服务运行状态和依赖项健康状况。",
    },
    {
        "name": "System",
        "description": "系统信息端点。提供应用版本、环境配置等运行时信息。",
    },
    {
        "name": "Authentication",
        "description": "认证与授权。包括用户注册、登录、JWT令牌管理。",
    },
    {
        "name": "Users",
        "description": "用户管理。美甲师账户的CRUD操作和个人信息管理。",
    },
    {
        "name": "Customers",
        "description": "客户档案管理。包括客户基本信息、详细档案（指甲特征、偏好等）。",
    },
    {
        "name": "Services",
        "description": "服务记录管理。记录服务过程、上传实际作品、美甲师复盘和客户反馈。",
    },
    {
        "name": "File Upload",
        "description": "文件上传服务。支持客户指甲照片、灵感图、设计图、实际完成图的上传。",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    redirect_slashes=False,
    description="""
## 美甲师能力成长系统 API

基于 AI 的美甲师能力追踪与设计生成平台。

### 核心功能

* **客户管理**: 维护客户档案，记录指甲特征、风格偏好
* **AI设计生成**: 基于客户档案和灵感图生成个性化设计方案（DALL-E 3）
* **设计微调**: 使用自然语言迭代优化设计（GPT-4 Vision）
* **服务记录**: 记录实际服务结果，包括照片和时长
* **AI对比分析**: 对比设计图与实际作品，识别差异（GPT-4 Vision）
* **能力追踪**: 构建多维度能力雷达图，追踪成长趋势

### 技术栈

* **Backend**: FastAPI + SQLAlchemy + Alembic
* **Database**: SQLite (开发) / PostgreSQL (生产)
* **AI**: OpenAI API (DALL-E 3 + GPT-4 Vision)
* **Storage**: 本地文件系统（图片存储于 `/uploads` 目录）

### 文档

* **Swagger UI**: [/docs](/docs) - 交互式API文档（仅 DEBUG 模式）
* **ReDoc**: [/redoc](/redoc) - API参考文档（仅 DEBUG 模式）
""",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_tags=tags_metadata,
    contact={
        "name": "Nail API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# 注册速率限制器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================
# 全局异常处理器
# ============================================

@app.exception_handler(NailAppException)
async def nail_app_exception_handler(request: Request, exc: NailAppException):
    """处理自定义应用异常"""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常（包括FastAPI的HTTPException）"""
    logger.warning(
        f"HTTP error: {exc.status_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误（Pydantic验证失败）"""
    logger.warning(
        f"Validation error: {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的所有其他异常"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# ============================================
# 中间件配置
# ============================================

# 日志中间件（记录所有请求）
app.add_middleware(LoggingMiddleware)

# CORS 中间件配置
# 注意：allow_origins=["*"] 与 allow_credentials=True 不兼容，浏览器会拒绝
if settings.DEBUG:
    # 开发模式：允许所有来源（Flutter Web 每次端口不同），不携带凭据
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # 生产模式：使用显式白名单，禁止通配符
    origins = settings.allowed_origins_list
    if "*" in origins:
        logger.warning(
            "ALLOWED_ORIGINS 包含通配符 '*'，生产环境存在安全风险，"
            "请在 .env 中设置具体的域名白名单"
        )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

# 挂载静态文件目录（用于提供上传的图片）
# 使用自定义子类在 ASGI 消息层注入安全头，防止 MIME 混淆攻击
class _SecureStaticFiles(StaticFiles):
    """在响应头中强制添加安全指令"""

    async def __call__(self, scope, receive, send):
        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message["headers"])
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"cache-control", b"private, max-age=3600"))
                message = {**message, "headers": headers}
            await send(message)

        await super().__call__(scope, receive, send_with_security_headers)


if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", _SecureStaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============================================
# 前端静态文件服务（Docker/Railway 部署时）
# ============================================
FRONTEND_DIR = "/app/frontend/web"

if os.path.exists(FRONTEND_DIR):
    # Flutter Web 静态资源目录挂载
    _assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="frontend_assets")
    _icons_dir = os.path.join(FRONTEND_DIR, "icons")
    if os.path.exists(_icons_dir):
        app.mount("/icons", StaticFiles(directory=_icons_dir), name="frontend_icons")

    logger.info(f"前端静态文件已挂载: {FRONTEND_DIR}")
else:
    # 无前端文件时（本地开发），显示 API 欢迎页
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME} API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }


# ============================================
# SPA Fallback Middleware（必须在所有路由之后）
# ============================================
if os.path.exists(FRONTEND_DIR):
    from starlette.responses import Response as StarletteResponse

    _index_html = os.path.join(FRONTEND_DIR, "index.html")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        response = await call_next(request)
        # 仅对 GET 请求 + 404/405 响应 + 非 API/非 uploads 路径做 SPA fallback
        path = request.url.path
        if (
            request.method == "GET"
            and response.status_code in (404, 405)
            and not path.startswith(("/api/", "/uploads/", "/docs", "/redoc", "/openapi.json", "/health"))
        ):
            # 先尝试返回静态文件
            file_path = os.path.join(FRONTEND_DIR, path.lstrip("/"))
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            # 否则返回 index.html（SPA 路由）
            if os.path.isfile(_index_html):
                return FileResponse(_index_html)
        return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
