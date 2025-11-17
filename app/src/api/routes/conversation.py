"""Conversation API routes following TDD specification."""
from datetime import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.conversation import Conversation
from src.services.conversation_service import ConversationService
from src.services.policy_service import PolicyService
from src.services.validation_service import ValidationService
from src.services.lead_service import LeadService
from src.repositories.policy_repository import PolicyRepository
from src.repositories.lead_repository import LeadRepository
from src.llm.providers.ollama_provider import OllamaProvider
from src.middleware.error_handler import SessionNotFoundError


router = APIRouter(prefix="/conversation", tags=["conversation"])


class StartConversationRequest(BaseModel):
    source: Optional[str] = "web"


class StartConversationResponse(BaseModel):
    session_id: str
    conversation_id: str
    welcome_message: str
    status: str


class MessagePayload(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    session_id: str
    response: str
    interest_detected: str
    conversation_stage: str
    metadata: dict


class EndConversationRequest(BaseModel):
    session_id: str
    reason: Optional[str] = None


class EndConversationResponse(BaseModel):
    session_id: str
    conversation_id: str
    status: str
    summary: str
    duration_seconds: int


class ConversationHistoryResponse(BaseModel):
    session_id: str
    conversation_id: str
    messages: list
    customer_profile: dict
    conversation_stage: str


def _create_conversation_service(db: AsyncSession) -> ConversationService:
    """Create conversation service with all dependencies."""
    llm_provider = OllamaProvider()
    policy_repo = PolicyRepository(db)
    policy_service = PolicyService(policy_repo)
    validation_service = ValidationService()
    lead_repo = LeadRepository(db)
    lead_service = LeadService(lead_repo)
    
    return ConversationService(
        db=db,
        llm_provider=llm_provider,
        policy_service=policy_service,
        validation_service=validation_service,
        lead_service=lead_service,
    )


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(
    request: StartConversationRequest = StartConversationRequest(),
    db: AsyncSession = Depends(get_db)
):
    """Start a new conversation."""
    service = _create_conversation_service(db)
    response = await service.start_conversation()
    
    return StartConversationResponse(
        session_id=response.session_id,
        conversation_id=response.conversation_id,
        welcome_message=response.message,
        status="started"
    )


@router.post("/message", response_model=MessageResponse)
async def send_message(
    payload: MessagePayload,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and receive response."""
    service = _create_conversation_service(db)
    
    try:
        response = await service.process_message(payload.session_id, payload.message)
        
        return MessageResponse(
            session_id=response.session_id,
            response=response.message,
            interest_detected=response.interest_detected.value if hasattr(response.interest_detected, 'value') else str(response.interest_detected),
            conversation_stage=response.conversation_stage.value if hasattr(response.conversation_stage, 'value') else str(response.conversation_stage),
            metadata=response.metadata or {}
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/end", response_model=EndConversationResponse)
async def end_conversation(
    payload: EndConversationRequest,
    db: AsyncSession = Depends(get_db),
):
    """End a conversation."""
    service = _create_conversation_service(db)
    
    try:
        result = await service.end_conversation(payload.session_id, payload.reason)
        
        return EndConversationResponse(
            session_id=result["session_id"],
            conversation_id=result["conversation_id"],
            status=result["status"],
            summary=result["summary"],
            duration_seconds=result["duration_seconds"]
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get conversation history."""
    from sqlalchemy import select
    from src.models.message import Message as MessageModel
    from src.services.session_manager import SessionManager
    
    # Get conversation
    res = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    res = await db.execute(
        select(MessageModel)
        .where(MessageModel.conversation_id == conv.id)
        .order_by(MessageModel.created_at.asc())
    )
    messages = res.scalars().all()
    
    # Get session state
    session_manager = SessionManager()
    state = await session_manager.get_session(session_id)
    
    customer_profile = {}
    if state:
        customer_profile = {
            "age": state.customer_profile.age,
            "name": state.customer_profile.name,
            "purpose": state.customer_profile.purpose,
            "dependents": state.customer_profile.dependents,
        }
    
    return ConversationHistoryResponse(
        session_id=session_id,
        conversation_id=str(conv.id),
        messages=[
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ],
        customer_profile=customer_profile,
        conversation_stage=conv.stage
    )
