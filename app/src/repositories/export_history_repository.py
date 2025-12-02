"""Repository for export history tracking."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.models.export_history import ExportHistory


class ExportHistoryRepository:
    """Repository for export history CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, export_history: ExportHistory) -> ExportHistory:
        """Create export history record."""
        self.session.add(export_history)
        await self.session.flush()
        return export_history
    
    async def list(
        self,
        export_type: Optional[str] = None,
        exported_by: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
    ) -> tuple[List[ExportHistory], int]:
        """
        List export history with filtering and pagination.
        
        Returns:
            Tuple of (export_history list, total count)
        """
        from sqlalchemy import and_
        
        # Build base query
        query = select(ExportHistory)
        count_query = select(func.count(ExportHistory.id))
        
        # Apply filters
        conditions = []
        
        if export_type:
            conditions.append(ExportHistory.export_type == export_type)
        
        if exported_by:
            conditions.append(ExportHistory.exported_by == exported_by)
        
        if start_date:
            conditions.append(ExportHistory.created_at >= start_date)
        
        if end_date:
            conditions.append(ExportHistory.created_at <= end_date)
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar_one()
        
        # Apply ordering, limit, and offset
        query = query.order_by(ExportHistory.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        # Execute query
        result = await self.session.execute(query)
        export_history = list(result.scalars().all())
        
        return export_history, total_count

