"""
日志中间件

记录所有HTTP请求和响应的日志，包括耗时统计。
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    记录每个HTTP请求的：
    - 请求方法、路径、查询参数
    - 客户端IP
    - 响应状态码
    - 请求耗时
    - 错误信息（如果有）
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()

        # 提取请求信息
        method = request.method
        url_path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"

        # 构建日志上下文
        log_context = {
            "method": method,
            "path": url_path,
            "client_ip": client_ip,
        }

        if query_params:
            log_context["query_params"] = query_params

        # 记录请求开始
        logger.info(
            f"Request started: {method} {url_path}",
            extra=log_context
        )

        # 处理请求
        try:
            response = await call_next(request)
        except Exception as exc:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {method} {url_path} - {str(exc)}",
                extra={
                    **log_context,
                    "process_time": f"{process_time:.3f}s",
                    "error": str(exc)
                },
                exc_info=True
            )
            raise

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加响应头（处理时间）
        # 尝试为所有响应类型添加响应头
        try:
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
        except Exception:
            # 某些响应类型可能不支持修改headers
            pass

        # 记录请求完成
        status_code = response.status_code
        log_level = logging.INFO

        # 根据状态码调整日志级别
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING

        logger.log(
            log_level,
            f"Request completed: {method} {url_path} - {status_code} ({process_time:.3f}s)",
            extra={
                **log_context,
                "status_code": status_code,
                "process_time": f"{process_time:.3f}s"
            }
        )

        return response
