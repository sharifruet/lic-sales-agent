from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class LeadStatus(str, Enum):
    """Lead status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    NOT_INTERESTED = "not_interested"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Collected fields
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    nid: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Interest & policy
    interested_policy: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Additional fields
    preferred_contact_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id"), nullable=True
    )
    
    # Status
    status: Mapped[LeadStatus] = mapped_column(
        String(20), 
        default=LeadStatus.NEW, 
        nullable=False,
        index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
