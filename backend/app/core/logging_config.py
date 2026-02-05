"""
日志配置

配置应用程序的日志系统，支持控制台和文件输出。
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional

from app.core.config import settings


# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 详细日志格式（包含文件名和行号）
DETAILED_LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "[%(filename)s:%(lineno)d] - %(message)s"
)


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> None:
    """
    配置应用程序日志

    Args:
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_dir: 日志文件目录（默认为 backend/logs）
        enable_file_logging: 是否启用文件日志
        enable_console_logging: 是否启用控制台日志
    """
    # 解析日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 清除现有处理器（避免重复）
    root_logger.handlers.clear()

    # 控制台处理器
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # 文件处理器
    if enable_file_logging:
        # 确定日志目录
        if log_dir is None:
            # 默认日志目录: backend/logs
            backend_dir = Path(__file__).parent.parent.parent
            log_dir = backend_dir / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)

        # 应用日志（所有级别）- 按大小轮转
        app_log_file = log_dir / "app.log"
        app_handler = RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        app_handler.setLevel(logging.INFO)
        app_formatter = logging.Formatter(DETAILED_LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        app_handler.setFormatter(app_formatter)
        root_logger.addHandler(app_handler)

        # 错误日志（ERROR及以上）- 按日期轮转
        error_log_file = log_dir / "error.log"
        error_handler = TimedRotatingFileHandler(
            error_log_file,
            when="midnight",
            interval=1,
            backupCount=30,  # 保留30天
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(DETAILED_LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)

    # 设置第三方库的日志级别（避免过多日志）
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称（通常使用 __name__）

    Returns:
        logging.Logger: 日志记录器实例

    Example:
        logger = get_logger(__name__)
        logger.info("This is an info message")
    """
    return logging.getLogger(name)


# 在模块导入时自动配置日志
if settings:
    log_level = getattr(settings, "LOG_LEVEL", "INFO")
    setup_logging(log_level=log_level)
else:
    # 如果settings未加载，使用默认配置
    setup_logging(log_level="INFO")
