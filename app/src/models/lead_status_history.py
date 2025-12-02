"""Lead status history model for audit logging."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class LeadStatusHistory(Base):
    """Track status changes for audit trail."""
    __tablename__ = "lead_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    
    previous_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(100), nullable=False)  # Username/admin ID
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Optional reason/notes

