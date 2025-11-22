"""Fallback response service for when critical services fail."""
from typing import Dict, Optional, Any
from src.services.session_manager import ConversationStage, InterestLevel


class FallbackService:
    """Service for generating fallback responses when LLM or other services fail."""
    
    # Fallback responses by conversation stage
    STAGE_FALLBACKS = {
        ConversationStage.INTRODUCTION: {
            "message": "Hello! I'm here to help you learn about life insurance. How can I assist you today?",
            "suggestions": ["Tell me about life insurance", "What policies do you offer?", "I need coverage"]
        },
        ConversationStage.QUALIFICATION: {
            "message": "I'd like to understand your needs better. Could you tell me a bit about your situation? For example, are you looking to protect your family, plan for retirement, or something else?",
            "suggestions": ["I want to protect my family", "I'm planning for retirement", "I need coverage for my business"]
        },
        ConversationStage.INFORMATION: {
            "message": "I can help you learn more about our life insurance options. Would you like information about term life, whole life, or universal life insurance?",
            "suggestions": ["Tell me about term life", "What's whole life insurance?", "I want to compare options"]
        },
        ConversationStage.PERSUASION: {
            "message": "Life insurance is an important way to protect your loved ones and provide financial security. Would you like to explore coverage options that fit your needs?",
            "suggestions": ["Show me options", "What coverage do I need?", "Tell me more"]
        },
        ConversationStage.OBJECTION_HANDLING: {
            "message": "I understand your concerns. Life insurance can seem complex, but I'm here to help answer any questions you have. What would you like to know more about?",
            "suggestions": ["Is it expensive?", "Do I need a medical exam?", "How does it work?"]
        },
        ConversationStage.INFORMATION_COLLECTION: {
            "message": "To help you get the best coverage, I'll need some basic information. This includes your name, contact information, and some details about your insurance needs. Shall we continue?",
            "suggestions": ["Yes, let's continue", "What information do you need?"]
        },
        ConversationStage.CLOSING: {
            "message": "Based on what you've told me, I believe we can find a policy that meets your needs. Would you like to proceed with getting a quote?",
            "suggestions": ["Yes, get me a quote", "Tell me more first"]
        },
        ConversationStage.ENDED: {
            "message": "Thank you for your time. If you have any questions in the future, please feel free to reach out. Have a great day!",
            "suggestions": []
        }
    }
    
    # Generic fallback responses
    GENERIC_FALLBACKS = [
        "I'm having a technical issue right now, but I'd still like to help. Could you rephrase your question or let me know what you'd like to know about life insurance?",
        "I'm experiencing a temporary technical problem. Please try asking your question again, or let me know if there's something specific about life insurance you'd like to learn about.",
        "I apologize for the technical issue. To better assist you, could you tell me what you're looking for? For example, are you interested in learning about our policies, getting a quote, or have specific questions?",
    ]
    
    # Fallback responses based on intent
    INTENT_FALLBACKS = {
        "greeting": "Hello! I'm here to help you with life insurance. How can I assist you today?",
        "question": "I'd be happy to answer your question. Could you please provide a bit more detail?",
        "interest": "That's great to hear! I'd love to help you find the right life insurance policy. What would you like to know more about?",
        "objection": "I understand your concerns. Let me try to address them. Could you tell me what specifically concerns you about life insurance?",
        "information_request": "I can provide information about our life insurance options. Are you interested in term life, whole life, or universal life insurance?",
    }
    
    def get_fallback_response(
        self,
        stage: Optional[ConversationStage] = None,
        intent: Optional[str] = None,
        interest_level: Optional[InterestLevel] = None,
        error_type: Optional[str] = None
    ) -> str:
        """
        Get a fallback response when LLM service fails.
        
        Args:
            stage: Current conversation stage
            intent: Detected intent (if available)
            interest_level: Customer interest level
            error_type: Type of error (for specific fallback)
        
        Returns:
            Fallback response message
        """
        # Use stage-specific fallback if available
        if stage and stage in self.STAGE_FALLBACKS:
            return self.STAGE_FALLBACKS[stage]["message"]
        
        # Use intent-specific fallback if available
        if intent and intent in self.INTENT_FALLBACKS:
            return self.INTENT_FALLBACKS[intent]
        
        # Use interest-level based fallback
        if interest_level:
            if interest_level == InterestLevel.HIGH:
                return "I'm currently experiencing a technical issue, but I'm very interested in helping you find the right life insurance policy. Could you please try asking your question again, or let me know what specific coverage you're looking for?"
            elif interest_level == InterestLevel.MEDIUM:
                return "I apologize for the technical difficulty. I'd still like to help you explore life insurance options. What would you like to know more about?"
            elif interest_level == InterestLevel.LOW:
                return "I'm having a temporary technical issue. If you're curious about life insurance, I'd be happy to answer any questions once the issue is resolved. Please try again in a moment."
        
        # Use generic fallback
        import random
        return random.choice(self.GENERIC_FALLBACKS)
    
    def get_llm_error_message(self, retry_after: Optional[int] = None) -> str:
        """
        Get user-friendly message for LLM service errors.
        
        Args:
            retry_after: Seconds until retry is suggested
        
        Returns:
            User-friendly error message
        """
        if retry_after:
            return f"I'm experiencing a temporary technical issue. Please try again in about {retry_after} seconds, or rephrase your question."
        return "I'm experiencing a temporary technical issue. Please try again in a moment, or rephrase your question."
    
    def get_database_error_message(self, operation: str = "save") -> str:
        """
        Get user-friendly message for database errors.
        
        Args:
            operation: Type of database operation
        
        Returns:
            User-friendly error message
        """
        if "save" in operation.lower() or "create" in operation.lower():
            return "I'm experiencing a temporary issue saving your information. Please try again in a moment, and your information will be saved."
        return "I'm experiencing a temporary technical issue. Please try again in a moment."
    
    def get_network_error_message(self) -> str:
        """Get user-friendly message for network errors."""
        return "I'm experiencing a temporary connectivity issue. Please try again in a moment."

