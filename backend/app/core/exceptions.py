from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class SmartMESException(Exception):
    """Base exception for all domain-specific application errors."""
    def __init__(self, message: str, code: str = "INTERNAL_SERVER_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(SmartMESException):
    def __init__(self, message: str = "Requested resource was not found"):
        super().__init__(message=message, code="RESOURCE_NOT_FOUND", status_code=404)


class UnauthorizedException(SmartMESException):
    def __init__(self, message: str = "Invalid credentials or token expired"):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)


class ForbiddenException(SmartMESException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


async def smartmes_exception_handler(request: Request, exc: SmartMESException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": str(request.url.path),
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "path": str(request.url.path),
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    raw_errors = exc.errors()
    sanitized_errors = []
    for err in raw_errors:
        err_copy = dict(err)
        if "ctx" in err_copy and isinstance(err_copy["ctx"], dict):
            err_copy["ctx"] = {k: str(v) for k, v in err_copy["ctx"].items()}
        sanitized_errors.append(err_copy)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": sanitized_errors,
                "path": str(request.url.path),
            }
        }
    )

