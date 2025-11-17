"""Context Manager for building LLM context."""
from typing import List, Dict, Optional
from src.llm.providers.llm_provider import Message
from src.services.session_manager import SessionState


class LLMContext:
    """LLM context container."""
    def __init__(self, messages: List[Message], metadata: Dict = None):
        self.messages = messages
        self.metadata = metadata or {}


class ContextManager:
    """Manages conversation context for LLM."""
    
    MAX_CONTEXT_MESSAGES = 50
    MAX_CONTEXT_TOKENS = 8000  # Conservative estimate
    
    def build_context(
        self,
        session: SessionState,
        customer_profile: Dict,
        policies: List[Dict],
        message_history: List[Dict] = None
    ) -> LLMContext:
        """Build context for LLM from session."""
        # Get recent messages (from message_history if provided, otherwise empty)
        if message_history:
            recent_messages = message_history[-self.MAX_CONTEXT_MESSAGES:]
        else:
            recent_messages = []
        
        # Build message list
        messages = []
        
        # Add summary of earlier conversation if exists
        if session.context_summary:
            messages.append(Message(
                role="system",
                content=f"Earlier conversation summary: {session.context_summary}"
            ))
        
        # Add customer profile
        if customer_profile:
            profile_text = self._format_profile(customer_profile)
            messages.append(Message(
                role="system",
                content=f"Customer profile: {profile_text}"
            ))
        
        # Add available policies (relevant ones only)
        if policies:
            policies_text = self._format_policies(policies)
            messages.append(Message(
                role="system",
                content=f"Available policies: {policies_text}"
            ))
        
        # Add conversation messages
        # Handle both dict format and object format
        for msg in recent_messages:
            if isinstance(msg, dict):
                messages.append(Message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
            else:
                # Assume it has role and content attributes
                messages.append(Message(
                    role=getattr(msg, "role", "user"),
                    content=getattr(msg, "content", "")
                ))
        
        # Check token count and summarize if needed
        estimated_tokens = self._estimate_tokens(messages)
        if estimated_tokens > self.MAX_CONTEXT_TOKENS:
            messages = self._compress_context(messages)
        
        return LLMContext(messages=messages, metadata={
            "session_id": session.session_id,
            "stage": session.conversation_stage.value if hasattr(session.conversation_stage, 'value') else str(session.conversation_stage)
        })
    
    def _format_profile(self, profile: Dict) -> str:
        """Format customer profile as text."""
        parts = []
        if profile.get("age"):
            parts.append(f"Age: {profile['age']}")
        if profile.get("name"):
            parts.append(f"Name: {profile['name']}")
        if profile.get("purpose"):
            parts.append(f"Purpose: {profile['purpose']}")
        if profile.get("dependents"):
            parts.append(f"Dependents: {profile['dependents']}")
        if profile.get("coverage_amount_interest"):
            parts.append(f"Coverage interest: {profile['coverage_amount_interest']}")
        return ", ".join(parts) if parts else "No profile information"
    
    def _format_policies(self, policies: List[Dict]) -> str:
        """Format policies as text."""
        if not policies:
            return "No policies available"
        
        formatted = []
        for policy in policies[:5]:  # Limit to top 5
            policy_str = f"- {policy.get('name', 'Unknown')}: "
            policy_str += f"Coverage: {policy.get('coverage_amount', 'N/A')}, "
            policy_str += f"Premium: ${policy.get('monthly_premium', 'N/A')}/month"
            formatted.append(policy_str)
        
        return "\n".join(formatted)
    
    def _estimate_tokens(self, messages: List[Message]) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4
    
    def _compress_context(self, messages: List[Message]) -> List[Message]:
        """Compress context by summarizing older messages."""
        # Keep system messages and last 30 messages
        system_msgs = [m for m in messages if m.role == "system"]
        recent_msgs = messages[-30:]
        
        middle_msgs = messages[len(system_msgs):-30]
        if middle_msgs:
            # Simple summary: just keep first and last of middle messages
            summary = f"Previous conversation ({len(middle_msgs)} messages): {middle_msgs[0].content[:100]}... {middle_msgs[-1].content[:100]}"
            system_msgs.append(Message(
                role="system",
                content=f"Conversation summary: {summary}"
            ))
        
        return system_msgs + recent_msgs

