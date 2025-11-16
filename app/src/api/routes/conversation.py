from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from src.database import get_db
from src.models.conversation import Conversation
from src.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversation", tags=["conversation"])


class StartResponse(BaseModel):
    session_id: str


class MessagePayload(BaseModel):
    session_id: str
    message: str


@router.post("/start", response_model=StartResponse)
async def start_conversation(db: AsyncSession = Depends(get_db)):
    session_id = uuid.uuid4().hex
    conv = Conversation(session_id=session_id, stage="introduction", created_at=datetime.utcnow())
    db.add(conv)
    await db.flush()
    return StartResponse(session_id=session_id)


@router.post("/message", response_model=dict)
async def send_message(payload: MessagePayload, db: AsyncSession = Depends(get_db)):
    service = ConversationService(db)
    reply = await service.process(payload.session_id, payload.message)
    return {"response": reply}
