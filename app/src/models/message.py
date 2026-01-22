from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(String, nullable=False)
    message_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)  # Optional metadata (intent, sentiment, entities, etc.)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
