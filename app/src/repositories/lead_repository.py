from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.lead import Lead
from src.models.lead_status_history import LeadStatusHistory


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

    async def list(
        self,
        status: Optional[str] = None,
        interested_policy: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[List[Lead], int]:
        """
        List leads with filtering, search, and pagination.
        
        Returns:
            Tuple of (leads list, total count)
        """
        from datetime import datetime
        from sqlalchemy import or_, func, and_
        
        # Build base query
        query = select(Lead)
        count_query = select(func.count(Lead.id))
        
        # Apply filters
        conditions = []
        
        if status:
            conditions.append(Lead.status == status.lower())
        
        if interested_policy:
            conditions.append(Lead.interested_policy.ilike(f"%{interested_policy}%"))
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                conditions.append(Lead.created_at >= start_dt)
            except:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                conditions.append(Lead.created_at <= end_dt)
            except:
                pass
        
        # Apply search (name, phone, email)
        if search:
            search_condition = or_(
                Lead.name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
            )
            conditions.append(search_condition)
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar_one()
        
        # Apply ordering, limit, and offset
        query = query.order_by(Lead.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        # Execute query
        result = await self.session.execute(query)
        leads = list(result.scalars().all())
        
        return leads, total_count

    async def update(self, lead_id: int, updates: dict) -> Optional[Lead]:
        """Update lead with partial updates."""
        from src.models.lead import LeadStatus
        
        lead = await self.find_by_id(lead_id)
        if not lead:
            return None
        
        for key, value in updates.items():
            if hasattr(lead, key) and value is not None:
                # Handle enum conversion for status field
                if key == "status" and isinstance(value, LeadStatus):
                    setattr(lead, key, value)
                else:
                    setattr(lead, key, value)
        
        # Update timestamp will be handled by SQLAlchemy onupdate
        await self.session.flush()
        return lead

    async def add_status_history(
        self,
        lead_id: int,
        previous_status: Optional[str],
        new_status: str,
        changed_by: str,
        notes: Optional[str] = None
    ) -> LeadStatusHistory:
        """Add status change to audit log."""
        history = LeadStatusHistory(
            lead_id=lead_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            notes=notes
        )
        self.session.add(history)
        await self.session.flush()
        return history

    async def get_status_history(
        self,
        lead_id: int,
        limit: Optional[int] = None
    ) -> List[LeadStatusHistory]:
        """Get status change history for a lead."""
        query = select(LeadStatusHistory).where(
            LeadStatusHistory.lead_id == lead_id
        ).order_by(LeadStatusHistory.changed_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def bulk_update_status(
        self,
        lead_ids: List[int],
        new_status: str,
        changed_by: str,
        notes: Optional[str] = None
    ) -> List[int]:
        """
        Bulk update status for multiple leads.
        
        Args:
            lead_ids: List of lead IDs to update
            new_status: New status value
            changed_by: User/admin who made the change
            notes: Optional notes for status change
        
        Returns:
            List of successfully updated lead IDs
        """
        from src.models.lead import LeadStatus
        
        if not lead_ids:
            return []
        
        # Convert string status to enum if needed
        if isinstance(new_status, str):
            try:
                status_enum = LeadStatus(new_status.lower())
            except ValueError:
                raise ValueError(f"Invalid status: {new_status}")
        else:
            status_enum = new_status
            new_status = status_enum.value
        
        # Find all leads
        query = select(Lead).where(Lead.id.in_(lead_ids))
        result = await self.session.execute(query)
        leads = list(result.scalars().all())
        
        updated_lead_ids = []
        
        # Update each lead and log status change
        for lead in leads:
            previous_status = lead.status.value if lead.status else None
            
            # Only update if status is different
            if previous_status != new_status:
                lead.status = status_enum
                await self.session.flush()
                
                # Log status change for audit trail
                await self.add_status_history(
                    lead_id=lead.id,
                    previous_status=previous_status,
                    new_status=new_status,
                    changed_by=changed_by,
                    notes=notes
                )
                
                updated_lead_ids.append(lead.id)
        
        return updated_lead_ids
