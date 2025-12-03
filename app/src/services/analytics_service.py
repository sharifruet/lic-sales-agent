"""Analytics service for conversation tracking and metrics."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.models.conversation import Conversation
from app.src.models.message import Message
from app.src.models.lead import Lead


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
        self.avg_time_in_stage: Dict[str, float] = {}  # Average time (seconds) spent in each stage
        self.stage_progression_patterns: Dict[str, int] = {}  # Common stage progression patterns


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
            
            # Calculate average time in each stage (AC-026.3)
            metrics.avg_time_in_stage = await self._calculate_avg_time_in_stage(conversations)
            
            # Calculate stage progression patterns (AC-026.3)
            metrics.stage_progression_patterns = await self._calculate_stage_progression_patterns(conversations)
            
            # Count conversations that resulted in leads
            conv_ids = [conv.id for conv in conversations]
            if conv_ids:
                leads_query = select(func.count(Lead.id)).where(Lead.conversation_id.in_(conv_ids))
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
    
    async def _calculate_avg_time_in_stage(
        self,
        conversations: List[Conversation]
    ) -> Dict[str, float]:
        """
        Calculate average time spent in each stage (AC-026.3).
        
        Since we don't have stage history, we estimate based on:
        - Conversations that ended in a stage: use their total duration
        - For active conversations: estimate based on current stage and duration
        """
        stage_durations: Dict[str, List[float]] = {}
        
        for conv in conversations:
            if not conv.created_at:
                continue
            
            # Calculate conversation duration
            end_time = conv.updated_at if conv.updated_at else datetime.utcnow()
            duration = (end_time - conv.created_at).total_seconds()
            
            if duration <= 0:
                continue
            
            stage = conv.stage or "unknown"
            
            # Group durations by stage
            if stage not in stage_durations:
                stage_durations[stage] = []
            stage_durations[stage].append(duration)
        
        # Calculate averages
        avg_times: Dict[str, float] = {}
        for stage, durations in stage_durations.items():
            if durations:
                avg_times[stage] = sum(durations) / len(durations)
            else:
                avg_times[stage] = 0.0
        
        return avg_times
    
    async def _calculate_stage_progression_patterns(
        self,
        conversations: List[Conversation]
    ) -> Dict[str, int]:
        """
        Calculate stage progression patterns (AC-026.3).
        
        Since we don't have full stage history, we infer patterns from:
        - Final stage reached (indicates progression depth)
        - Common stage transitions based on final stage
        """
        # Track final stages reached
        final_stages: Dict[str, int] = {}
        
        # Define typical progression stages
        stage_order = [
            "introduction",
            "qualification",
            "information",
            "persuasion",
            "objection_handling",
            "information_collection",
            "closing",
            "ended"
        ]
        
        for conv in conversations:
            final_stage = conv.stage or "unknown"
            
            # Count how many conversations reached each stage
            if final_stage not in final_stages:
                final_stages[final_stage] = 0
            final_stages[final_stage] += 1
        
        # Build progression patterns based on final stage
        # Pattern format: "introduction->qualification->information" etc.
        patterns: Dict[str, int] = {}
        
        for final_stage, count in final_stages.items():
            if final_stage in stage_order:
                # Build progression path up to final stage
                final_index = stage_order.index(final_stage)
                progression = "->".join(stage_order[:final_index + 1])
                patterns[progression] = patterns.get(progression, 0) + count
            else:
                # Unknown or custom stage
                patterns[f"unknown->{final_stage}"] = patterns.get(f"unknown->{final_stage}", 0) + count
        
        return patterns
    
    async def get_conversation_quality_score(self, conversation_id: int) -> float:
        """
        Calculate quality score for a conversation (AC-026.4).
        
        Quality factors:
        - Conversation completeness (reached closing/ended stage)
        - Customer engagement (message count, interaction)
        - Information collected (lead generated)
        - Outcome (lead generated or not)
        """
        # Get conversation
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await self.db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            return 0.0
        
        # Get conversation messages
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            return 0.0
        
        # Quality factors
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]
        
        # 1. Engagement score (AC-026.4: Customer engagement)
        engagement_score = min(len(user_messages) / 10.0, 1.0)  # More messages = better engagement
        
        # 2. Balance score (conversation flow)
        balance_score = min(len(assistant_messages) / max(len(user_messages), 1), 1.0)  # Balanced conversation
        
        # 3. Length score (conversation depth)
        length_score = min(sum(len(m.content) for m in messages) / 2000.0, 1.0)  # Adequate length
        
        # 4. Completeness score (AC-026.4: Conversation completeness)
        # Check if conversation reached a meaningful stage
        final_stage = conversation.stage or "unknown"
        completeness_stages = ["closing", "ended", "information_collection"]
        completeness_score = 1.0 if final_stage in completeness_stages else 0.5
        
        # 5. Information collected score (AC-026.4: Information collected)
        # Check if lead was generated (indicates information was collected)
        lead_query = select(func.count(Lead.id)).where(Lead.conversation_id == conversation_id)
        lead_result = await self.db.execute(lead_query)
        lead_count = lead_result.scalar() or 0
        information_score = 1.0 if lead_count > 0 else 0.3  # Higher score if lead generated
        
        # 6. Outcome score (AC-026.4: Outcome - lead generated or not)
        outcome_score = 1.0 if lead_count > 0 else 0.2  # High score if lead generated
        
        # Weighted average (engagement, balance, length, completeness, information, outcome)
        quality_score = (
            engagement_score * 0.2 +
            balance_score * 0.15 +
            length_score * 0.15 +
            completeness_score * 0.2 +
            information_score * 0.15 +
            outcome_score * 0.15
        )
        
        return quality_score * 100  # Return as percentage
    
    async def get_conversation_quality_breakdown(self, conversation_id: int) -> Dict[str, float]:
        """
        Get detailed quality score breakdown for a conversation (AC-026.4).
        
        Returns breakdown of quality factors for actionable insights.
        """
        # Get conversation
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await self.db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            return {}
        
        # Get conversation messages
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            return {}
        
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]
        
        # Calculate individual scores
        engagement_score = min(len(user_messages) / 10.0, 1.0) * 100
        balance_score = min(len(assistant_messages) / max(len(user_messages), 1), 1.0) * 100
        length_score = min(sum(len(m.content) for m in messages) / 2000.0, 1.0) * 100
        
        # Completeness
        final_stage = conversation.stage or "unknown"
        completeness_stages = ["closing", "ended", "information_collection"]
        completeness_score = 100.0 if final_stage in completeness_stages else 50.0
        
        # Information collected
        lead_query = select(func.count(Lead.id)).where(Lead.conversation_id == conversation_id)
        lead_result = await self.db.execute(lead_query)
        lead_count = lead_result.scalar() or 0
        information_score = 100.0 if lead_count > 0 else 30.0
        
        # Outcome
        outcome_score = 100.0 if lead_count > 0 else 20.0
        
        return {
            "engagement_score": round(engagement_score, 2),
            "balance_score": round(balance_score, 2),
            "length_score": round(length_score, 2),
            "completeness_score": round(completeness_score, 2),
            "information_collected_score": round(information_score, 2),
            "outcome_score": round(outcome_score, 2),
            "lead_generated": lead_count > 0,
            "final_stage": final_stage,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages)
        }

