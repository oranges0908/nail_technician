"""
自定义异常类

定义应用程序的异常层次结构，方便统一处理错误。
"""
from typing import Any, Dict, Optional


class NailAppException(Exception):
    """
    应用程序基础异常类

    所有自定义异常都应继承此类
    """
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class AuthenticationError(NailAppException):
    """
    认证错误

    用于登录失败、token无效等认证相关错误
    """
    def __init__(self, message: str = "认证失败", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, detail=detail)


class AuthorizationError(NailAppException):
    """
    授权错误

    用于权限不足等授权相关错误
    """
    def __init__(self, message: str = "权限不足", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, detail=detail)


class ResourceNotFoundError(NailAppException):
    """
    资源未找到错误

    用于查询的资源不存在
    """
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} 不存在"
        detail = {"resource": resource}
        if resource_id:
            message = f"{resource} (ID: {resource_id}) 不存在"
            detail["resource_id"] = resource_id
        super().__init__(message, status_code=404, detail=detail)


class ResourceConflictError(NailAppException):
    """
    资源冲突错误

    用于创建重复资源（如邮箱已存在）
    """
    def __init__(self, message: str = "资源冲突", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, detail=detail)


class FileUploadError(NailAppException):
    """
    文件上传错误

    用于文件上传相关错误（类型不支持、大小超限等）
    """
    def __init__(self, message: str = "文件上传失败", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, detail=detail)


class AIServiceError(NailAppException):
    """
    AI服务错误

    用于AI服务调用失败（OpenAI API错误、配置错误等）
    """
    def __init__(self, message: str = "AI服务调用失败", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, detail=detail)


class DatabaseError(NailAppException):
    """
    数据库错误

    用于数据库操作失败
    """
    def __init__(self, message: str = "数据库操作失败", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, detail=detail)


class ValidationError(NailAppException):
    """
    数据验证错误

    用于业务逻辑验证失败（区别于Pydantic的RequestValidationError）
    """
    def __init__(self, message: str = "数据验证失败", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, detail=detail)


class ExternalServiceError(NailAppException):
    """
    外部服务错误

    用于调用外部服务失败（文件存储服务、第三方API等）
    """
    def __init__(self, service: str, message: str = "外部服务调用失败", detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["service"] = service
        super().__init__(message, status_code=502, detail=detail)
