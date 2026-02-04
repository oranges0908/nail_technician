from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from app.core.config import settings
from typing import Generator
import logging

logger = logging.getLogger(__name__)


# 根据数据库类型配置连接参数
def get_engine_config():
    """根据数据库类型返回引擎配置"""
    config = {
        "pool_pre_ping": True,  # 连接池健康检查
        "echo": settings.DEBUG,  # 开发环境打印 SQL
    }

    # SQLite 配置
    if "sqlite" in settings.DATABASE_URL:
        config["connect_args"] = {"check_same_thread": False}
        config["poolclass"] = StaticPool  # SQLite 使用静态池
    # PostgreSQL/MySQL 配置
    else:
        config["poolclass"] = QueuePool
        config["pool_size"] = 5  # 连接池大小
        config["max_overflow"] = 10  # 最大溢出连接数
        config["pool_timeout"] = 30  # 连接超时(秒)
        config["pool_recycle"] = 3600  # 连接回收时间(秒)

    return config


# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, **get_engine_config())

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 数据库依赖注入
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖注入函数，提供数据库会话

    Yields:
        Session: SQLAlchemy 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# 数据库健康检查
def check_db_health() -> bool:
    """
    检查数据库连接是否正常

    Returns:
        bool: 数据库连接是否正常
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# 创建所有表（仅用于测试，生产环境使用 Alembic）
def create_tables():
    """
    创建所有数据库表

    注意: 仅用于测试环境，生产环境应使用 Alembic 迁移
    """
    logger.warning("Creating tables directly (not recommended for production)")
    Base.metadata.create_all(bind=engine)


# 删除所有表（仅用于测试）
def drop_tables():
    """
    删除所有数据库表

    注意: 仅用于测试环境
    """
    logger.warning("Dropping all tables")
    Base.metadata.drop_all(bind=engine)
