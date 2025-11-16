from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.llm.providers.base import OllamaProvider
from src.models.message import Message
from src.models.conversation import Conversation


class ConversationService:
    def __init__(self, db: AsyncSession, llm: Optional[OllamaProvider] = None):
        self.db = db
        self.llm = llm or OllamaProvider()

    async def process(self, session_id: str, user_message: str) -> str:
        # Save user message
        conv_id = await self._get_conversation_id(session_id)
        self.db.add(Message(conversation_id=conv_id, role="user", content=user_message))
        await self.db.flush()

        # Call LLM (fallback to echo on error)
        try:
            reply = await self.llm.generate(user_message)
        except Exception:
            reply = f"You said: {user_message}"

        # Save assistant message
        self.db.add(Message(conversation_id=conv_id, role="assistant", content=reply))
        await self.db.flush()
        return reply

    async def _get_conversation_id(self, session_id: str) -> int:
        from sqlalchemy import select
        res = await self.db.execute(select(Conversation.id).where(Conversation.session_id == session_id))
        row = res.first()
        if not row:
            raise ValueError("Invalid session_id")
        return row[0]
