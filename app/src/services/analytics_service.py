"""Analytics service for conversation tracking and metrics."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message
from src.models.lead import Lead


class ConversationMetrics:
    """Conversation metrics data class."""
    def __init__(self):
        self.total_conversations = 0
        self.total_messages = 0
        self.avg_conversation_duration = 0.0
        self.avg_messages_per_conversation = 0.0
        self.conversations_by_stage: Dict[str, int] = {}
        self.conversations_by_interest: Dict[str, int] = {}
        self.conversion_rate = 0.0


class AnalyticsService:
    """Service for analytics and metrics tracking."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_conversation_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ConversationMetrics:
        """Get overall conversation metrics."""
        metrics = ConversationMetrics()
        
        # Build query
        query = select(Conversation)
        if start_date:
            query = query.where(Conversation.created_at >= start_date)
        if end_date:
            query = query.where(Conversation.created_at <= end_date)
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        metrics.total_conversations = len(conversations)
        
        if conversations:
            # Calculate totals and averages
            total_duration = sum(
                (conv.updated_at - conv.created_at).total_seconds()
                for conv in conversations
                if conv.updated_at and conv.created_at
            )
            metrics.avg_conversation_duration = total_duration / len(conversations) if conversations else 0
            
            total_messages = sum(conv.message_count for conv in conversations)
            metrics.total_messages = total_messages
            metrics.avg_messages_per_conversation = total_messages / len(conversations) if conversations else 0
            
            # Count by stage
            stage_counts: Dict[str, int] = {}
            for conv in conversations:
                stage = conv.stage or "unknown"
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            metrics.conversations_by_stage = stage_counts
            
            # Count conversations that resulted in leads
            conv_ids = [conv.id for conv in conversations]
            if conv_ids:
                leads_query = select(func.count(Lead.id)).where(Lead.id.in_(conv_ids))
                leads_result = await self.db.execute(leads_query)
                lead_count = leads_result.scalar() or 0
                metrics.conversion_rate = (lead_count / len(conversations)) * 100
        
        return metrics
    
    async def get_conversation_timeline(
        self,
        days: int = 7
    ) -> List[Dict]:
        """Get conversation timeline data."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(Conversation).where(
            Conversation.created_at >= start_date
        ).order_by(Conversation.created_at)
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        timeline = []
        for conv in conversations:
            timeline.append({
                "date": conv.created_at.isoformat(),
                "conversations": 1,
                "messages": conv.message_count,
                "stage": conv.stage
            })
        
        return timeline
    
    async def get_lead_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get lead generation metrics."""
        query = select(Lead)
        if start_date:
            query = query.where(Lead.created_at >= start_date)
        if end_date:
            query = query.where(Lead.created_at <= end_date)
        
        result = await self.db.execute(query)
        leads = result.scalars().all()
        
        total_leads = len(leads)
        qualified_leads = sum(1 for lead in leads if lead.is_qualified)
        
        # Group by policy interest
        policy_counts: Dict[str, int] = {}
        for lead in leads:
            policy = lead.interested_policy or "none"
            policy_counts[policy] = policy_counts.get(policy, 0) + 1
        
        return {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "qualification_rate": (qualified_leads / total_leads * 100) if total_leads > 0 else 0,
            "leads_by_policy": policy_counts
        }
    
    async def get_conversation_quality_score(self, conversation_id: int) -> float:
        """Calculate quality score for a conversation."""
        # Get conversation messages
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            return 0.0
        
        # Simple quality metrics
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]
        
        # Quality factors
        engagement_score = min(len(user_messages) / 10.0, 1.0)  # More messages = better engagement
        balance_score = len(assistant_messages) / max(len(user_messages), 1)  # Balanced conversation
        length_score = min(sum(len(m.content) for m in messages) / 2000.0, 1.0)  # Adequate length
        
        # Average score
        quality_score = (engagement_score + balance_score + length_score) / 3.0
        
        return quality_score * 100  # Return as percentage

