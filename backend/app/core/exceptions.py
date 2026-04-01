"""
Custom exception classes

Defines the application exception hierarchy for unified error handling.
"""
from typing import Any, Dict, Optional


class NailAppException(Exception):
    """
    Base application exception class

    All custom exceptions should inherit from this class
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
    """Authentication error for login failures, invalid tokens, etc."""
    def __init__(self, message: str = "Authentication failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, detail=detail)


class AuthorizationError(NailAppException):
    """Authorization error for insufficient permissions."""
    def __init__(self, message: str = "Insufficient permissions", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, detail=detail)


class ResourceNotFoundError(NailAppException):
    """Resource not found error."""
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} not found"
        detail = {"resource": resource}
        if resource_id:
            message = f"{resource} (ID: {resource_id}) not found"
            detail["resource_id"] = resource_id
        super().__init__(message, status_code=404, detail=detail)


class ResourceConflictError(NailAppException):
    """Resource conflict error for duplicate resources (e.g. email already exists)."""
    def __init__(self, message: str = "Resource conflict", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, detail=detail)


class FileUploadError(NailAppException):
    """File upload error (unsupported type, size exceeded, etc.)."""
    def __init__(self, message: str = "File upload failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, detail=detail)


class AIServiceError(NailAppException):
    """AI service error for failed AI service calls (OpenAI API errors, config errors, etc.)."""
    def __init__(self, message: str = "AI service call failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, detail=detail)


class DatabaseError(NailAppException):
    """Database error for failed database operations."""
    def __init__(self, message: str = "Database operation failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, detail=detail)


class ValidationError(NailAppException):
    """Data validation error for business logic validation failures (distinct from Pydantic's RequestValidationError)."""
    def __init__(self, message: str = "Data validation failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, detail=detail)


class ExternalServiceError(NailAppException):
    """External service error for failed calls to external services (file storage, third-party APIs, etc.)."""
    def __init__(self, service: str, message: str = "External service call failed", detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["service"] = service
        super().__init__(message, status_code=502, detail=detail)
