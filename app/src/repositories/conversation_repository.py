"""Conversation repository for database operations."""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationRepository:
    """Repository for conversation and message CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, conversation: Conversation) -> Conversation:
        """Create new conversation."""
        self.session.add(conversation)
        await self.session.flush()
        return conversation
    
    async def find_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Find conversation by ID."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    async def find_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Find conversation by session ID."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add message to conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=metadata,  # Store metadata if provided
        )
        self.session.add(message)
        await self.session.flush()
        return message
    
    async def get_messages(
        self,
        conversation_id: int,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get messages for conversation."""
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update(
        self,
        conversation_id: int,
        updates: Dict
    ) -> Optional[Conversation]:
        """Update conversation with partial updates."""
        conversation = await self.find_by_id(conversation_id)
        if not conversation:
            return None
        
        for key, value in updates.items():
            if hasattr(conversation, key) and value is not None:
                setattr(conversation, key, value)
        
        # Update timestamp will be handled by SQLAlchemy onupdate
        await self.session.flush()
        return conversation
    
    async def list(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Conversation]:
        """List conversations with optional pagination."""
        query = select(Conversation).order_by(Conversation.created_at.desc())
        
        if offset > 0:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

