from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os

_WEAK_SECRET_KEYS = {
    "",
    "your-secret-key-change-in-production",
    "your-secret-key-here-change-in-production",
    "secret",
    "changeme",
    "password",
}


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Nail"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # 默认关闭，开发时在 .env 中设置 DEBUG=True
    API_V1_PREFIX: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./nail.db"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # JWT 配置 - SECRET_KEY 必须在 .env 中设置为强随机值
    # 生成方式: openssl rand -hex 32
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS 配置 - 逗号分隔的字符串，如 "http://localhost:3000,http://localhost:8080"
    # 生产环境必须设置为具体的域名，不能使用 "*"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:9000"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v.lower() in _WEAK_SECRET_KEYS:
            raise ValueError(
                "SECRET_KEY 不安全或未设置。请在 .env 中配置强随机密钥。\n"
                "生成方式: openssl rand -hex 32"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY 长度不得少于 32 个字符")
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # 文件上传
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"

    # AI Provider 配置
    AI_PROVIDER: str = "openai"  # openai/gemini/baidu/alibaba
    OPENAI_API_KEY: str = ""  # 必须在 .env 中设置
    GEMINI_API_KEY: str = ""  # Google Gemini API Key

    # 邀请码配置（注册时必须填写，留空则任何人都可注册）
    INVITE_CODE: str = ""

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
