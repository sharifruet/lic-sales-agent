from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False, default="introduction")
    customer_profile_json: Mapped[str] = mapped_column(String, nullable=False, default="{}")

    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
