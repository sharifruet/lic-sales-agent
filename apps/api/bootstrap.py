"""API application factory integrating shared configuration and bootstrapping."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.cache import redis_manager
from config.database import init_db
from config.settings import settings
from .router import api_router
from tools import register_default_tools


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage startup and shutdown tasks."""
    await init_db()
    await redis_manager.connect()
    try:
        yield
    finally:
        await redis_manager.disconnect()


def create_api_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    register_default_tools()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered conversational life insurance sales agent",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/")
    async def root():
        return {
            "message": "AI Life Insurance Sales Agent API",
            "version": settings.app_version,
            "docs": "/docs",
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    return app

