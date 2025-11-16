"""Main API router configuration."""
from fastapi import APIRouter

from src.api.routes.leads import router as leads_router
from src.api.routes.conversation import router as conversation_router

# Create main router
api_router = APIRouter(prefix="/api", tags=["api"])

# Mount sub-routers
api_router.include_router(leads_router)
api_router.include_router(conversation_router)


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {"message": "AI Life Insurance Sales Agent API", "version": "1.0.0"}

