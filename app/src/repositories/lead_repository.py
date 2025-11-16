from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.lead import Lead


class LeadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, lead: Lead) -> Lead:
        self.session.add(lead)
        await self.session.flush()
        return lead

    async def find_by_id(self, lead_id: int) -> Optional[Lead]:
        res = await self.session.execute(select(Lead).where(Lead.id == lead_id))
        return res.scalar_one_or_none()

    async def find_by_phone(self, phone: str) -> Optional[Lead]:
        res = await self.session.execute(select(Lead).where(Lead.phone == phone))
        return res.scalar_one_or_none()

    async def list(self) -> List[Lead]:
        res = await self.session.execute(select(Lead).order_by(Lead.created_at.desc()))
        return list(res.scalars().all())
