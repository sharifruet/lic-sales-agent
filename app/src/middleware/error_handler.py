"""Error handling middleware for FastAPI."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Base application error."""
    pass


class ValidationError(ApplicationError):
    """Data validation error."""
    def __init__(self, message: str, errors: list = None):
        self.message = message
        self.errors = errors or []
        super().__init__(message)


class SessionNotFoundError(ApplicationError):
    """Session not found error."""
    pass


class LLMAPIError(ApplicationError):
    """LLM API error."""
    pass


class LLMRateLimitError(LLMAPIError):
    """LLM rate limit exceeded."""
    pass


class DuplicateLeadError(ApplicationError):
    """Duplicate lead detected."""
    pass


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Invalid input data",
            "details": errors
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail
        }
    )


async def application_error_handler(request: Request, exc: ApplicationError):
    """Handle application errors."""
    logger.error(f"Application error: {type(exc).__name__} - {str(exc)}", exc_info=True)
    
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "validation_error",
                "message": exc.message,
                "details": exc.errors
            }
        )
    
    if isinstance(exc, SessionNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "session_not_found",
                "message": "Session not found or expired"
            }
        )
    
    if isinstance(exc, LLMRateLimitError):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "message": "I'm processing too many requests. Please try again in a moment.",
                "retry_after": 60
            }
        )
    
    if isinstance(exc, LLMAPIError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "llm_service_error",
                "message": "I'm having a technical issue. Please try again in a moment.",
                "retry_after": 5
            }
        )
    
    if isinstance(exc, DuplicateLeadError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "duplicate_lead",
                "message": "A lead with this information already exists"
            }
        )
    
    # Generic application error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "application_error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.exception(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

