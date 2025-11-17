from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.policy import Policy


class PolicyRepository:
    """Basic repository for policy CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, policy: Policy) -> Policy:
        self.session.add(policy)
        await self.session.flush()
        return policy

    async def find_by_id(self, policy_id: int) -> Optional[Policy]:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[Policy]:
        result = await self.session.execute(
            select(Policy).where(Policy.name == name)
        )
        return result.scalar_one_or_none()

    async def list(self) -> List[Policy]:
        result = await self.session.execute(
            select(Policy).order_by(Policy.created_at.desc())
        )
        return list(result.scalars().all())


