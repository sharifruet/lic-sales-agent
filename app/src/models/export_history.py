"""Export history model for tracking lead exports."""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class ExportHistory(Base):
    """Model for tracking export history."""
    __tablename__ = "export_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Export details
    export_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'leads' or 'conversation'
    format: Mapped[str] = mapped_column(String(10), nullable=False)  # 'csv', 'json', 'pdf', 'txt'
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Filter criteria (stored as JSON string)
    filter_criteria: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of filters
    
    # User who performed export
    exported_by: Mapped[str] = mapped_column(String(120), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

