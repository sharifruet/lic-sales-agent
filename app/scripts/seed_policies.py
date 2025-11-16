import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models.policy import Policy


async def seed():
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        items = [
            Policy(name="Basic Term 250k", provider="AcmeLife", coverage_amount=250_000, monthly_premium=29.99, term_years=20, medical_exam_required=False, created_at=datetime.utcnow()),
            Policy(name="Family Term 500k", provider="AcmeLife", coverage_amount=500_000, monthly_premium=54.50, term_years=20, medical_exam_required=True, created_at=datetime.utcnow()),
            Policy(name="Premium Term 1M", provider="BestLife", coverage_amount=1_000_000, monthly_premium=120.00, term_years=30, medical_exam_required=True, created_at=datetime.utcnow()),
        ]
        for p in items:
            exists = await session.execute(select(Policy).where(Policy.name == p.name))
            if not exists.scalar_one_or_none():
                session.add(p)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
