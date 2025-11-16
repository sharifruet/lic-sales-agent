from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Collected fields
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    nid: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Interest & policy
    interested_policy: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
