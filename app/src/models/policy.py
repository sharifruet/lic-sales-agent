from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)

    coverage_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_premium: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    term_years: Mapped[int] = mapped_column(Integer, nullable=False)
    medical_exam_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
