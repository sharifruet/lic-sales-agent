"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from sqlalchemy import select
from redis import asyncio as redis_async
import httpx
import os
from src.config import settings
from src.api.router import api_router
from src.database import engine
from src.middleware.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    application_error_handler,
    generic_exception_handler,
    ApplicationError,
)
from src.middleware.rate_limiter import RateLimitMiddleware

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered conversational life insurance sales agent (Text & Voice)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (optional - can be disabled for development)
if settings.enable_rate_limiting:
    app.add_middleware(RateLimitMiddleware)

# Error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routers
app.include_router(api_router)

# Mount static files for frontend
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Root endpoint - serves frontend if available, otherwise returns API info."""
    static_index = os.path.join(static_dir, "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {
        "message": "AI Life Insurance Sales Agent API",
        "version": settings.app_version,
        "docs": "/docs",
    }


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str  # "healthy" or "degraded"
    version: str
    database: str  # "ok" or "error"
    redis: str  # "ok" or "error"
    llm_provider: str  # "ok" or "error"
    environment: str = "development"


@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Enhanced health check endpoint with database, Redis, and LLM provider checks.
    
    Returns:
        - status: "healthy" if all services are ok, "degraded" otherwise
        - database: "ok" or "error"
        - redis: "ok" or "error"
        - llm_provider: "ok" or "error"
    """
    # Check database connectivity
    db_status = "ok"
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
    except Exception:
        db_status = "error"
    
    # Check Redis connectivity
    redis_status = "ok"
    try:
        redis_client = redis_async.from_url(
            settings.redis_url,
            password=settings.redis_password,
            decode_responses=True
        )
        await redis_client.ping()
        await redis_client.close()
    except Exception:
        redis_status = "error"
    
    # Check LLM provider status
    llm_status = "ok"
    try:
        if settings.llm_provider == "ollama":
            # Check Ollama is reachable
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.ollama_base_url}/api/tags",
                    timeout=5.0
                )
                if response.status_code != 200:
                    llm_status = "error"
        elif settings.llm_provider == "openai":
            # Check OpenAI API key is configured
            if not settings.openai_api_key:
                llm_status = "error"
            else:
                # Optionally test API key (can be slow, so just check presence)
                pass  # API key is present
        elif settings.llm_provider == "anthropic":
            # Check Anthropic API key is configured
            if not settings.anthropic_api_key:
                llm_status = "error"
            else:
                # Optionally test API key (can be slow, so just check presence)
                pass  # API key is present
        else:
            llm_status = "error"  # Unknown provider
    except Exception:
        llm_status = "error"
    
    # Determine overall status
    overall_status = "healthy" if all([
        db_status == "ok",
        redis_status == "ok",
        llm_status == "ok"
    ]) else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        version=settings.app_version,
        database=db_status,
        redis=redis_status,
        llm_provider=llm_status,
        environment=settings.environment
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

