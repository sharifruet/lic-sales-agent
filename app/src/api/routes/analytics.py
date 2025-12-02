"""Analytics API routes."""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from app.src.services.analytics_service import AnalyticsService
from app.src.middleware.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/conversations")
async def get_conversation_analytics(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """Get conversation analytics (admin only)."""
    service = AnalyticsService(db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    metrics = await service.get_conversation_metrics(start_date=start_date)
    
    return {
        "period_days": days,
        "total_conversations": metrics.total_conversations,
        "total_messages": metrics.total_messages,
        "avg_conversation_duration_seconds": metrics.avg_conversation_duration,
        "avg_messages_per_conversation": metrics.avg_messages_per_conversation,
        "conversations_by_stage": metrics.conversations_by_stage,
        "avg_time_in_stage_seconds": metrics.avg_time_in_stage,  # AC-026.3: Average time in each stage
        "stage_progression_patterns": metrics.stage_progression_patterns,  # AC-026.3: Stage progression patterns
        "conversion_rate_percent": metrics.conversion_rate
    }


@router.get("/leads")
async def get_lead_analytics(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """Get lead generation analytics (admin only)."""
    service = AnalyticsService(db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    metrics = await service.get_lead_metrics(start_date=start_date)
    
    return {
        "period_days": days,
        **metrics
    }


@router.get("/timeline")
async def get_conversation_timeline(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """Get conversation timeline data (admin only)."""
    service = AnalyticsService(db)
    
    timeline = await service.get_conversation_timeline(days=days)
    
    return {
        "period_days": days,
        "timeline": timeline
    }


@router.get("/conversation/{conversation_id}/quality")
async def get_conversation_quality(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)  # Admin only
):
    """Get quality score for a conversation (admin only)."""
    service = AnalyticsService(db)
    
    score = await service.get_conversation_quality_score(conversation_id)
    
    # Get detailed quality breakdown (AC-026.4: Quality score breakdown)
    service = AnalyticsService(db)
    quality_breakdown = await service.get_conversation_quality_breakdown(conversation_id)
    
    return {
        "conversation_id": conversation_id,
        "quality_score": score,
        "rating": "excellent" if score >= 80 else "good" if score >= 60 else "fair" if score >= 40 else "poor",
        "breakdown": quality_breakdown  # AC-026.4: Quality score breakdown
    }

