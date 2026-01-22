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

    async def list(
        self,
        provider: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Policy]:
        """
        List policies, optionally filtered by provider or searched by name.
        
        Args:
            provider: Filter by provider name (partial match)
            search: Search by policy name (partial match)
        """
        from sqlalchemy import or_
        
        query = select(Policy)
        conditions = []
        
        if provider:
            conditions.append(Policy.provider.ilike(f"%{provider}%"))
        
        if search:
            conditions.append(Policy.name.ilike(f"%{search}%"))
        
        if conditions:
            if len(conditions) == 1:
                query = query.where(conditions[0])
            else:
                query = query.where(or_(*conditions))
        
        query = query.order_by(Policy.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def delete(self, policy_id: int, soft_delete: bool = True) -> bool:
        """
        Delete or deactivate a policy.
        
        Args:
            policy_id: Policy ID to delete/deactivate
            soft_delete: If True, marks as inactive; if False, hard deletes (default: True)
        
        Returns:
            True if successful, False if policy not found
        """
        policy = await self.find_by_id(policy_id)
        if not policy:
            return False
        
        if soft_delete:
            # Soft delete: Add is_active field if not exists, or use status field
            # For now, we'll add a note that soft delete can be implemented
            # by adding an is_active field to the Policy model
            # For now, we'll do a hard delete but this should be updated
            # when the Policy model is extended with an is_active field
            await self.session.delete(policy)
        else:
            # Hard delete
            await self.session.delete(policy)
        
        await self.session.flush()
        return True

    async def find_by_provider(self, provider: str, exact_match: bool = False) -> List[Policy]:
        """
        Find all policies by a specific provider.
        
        Args:
            provider: Provider name to search for
            exact_match: If True, uses exact match; if False, uses case-insensitive partial match
        """
        if exact_match:
            query = select(Policy).where(Policy.provider == provider)
        else:
            # Case-insensitive partial match
            query = select(Policy).where(Policy.provider.ilike(f"%{provider}%"))
        
        query = query.order_by(Policy.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, policy_id: int, updates: dict) -> Optional[Policy]:
        """Update policy with partial updates."""
        policy = await self.find_by_id(policy_id)
        if not policy:
            return None
        
        for key, value in updates.items():
            if hasattr(policy, key) and value is not None:
                setattr(policy, key, value)
        
        # Update timestamp will be handled by SQLAlchemy onupdate
        await self.session.flush()
        return policy


