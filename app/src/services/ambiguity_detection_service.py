"""Ambiguity Detection Service for handling unclear or ambiguous user inputs."""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from app.src.llm.providers.llm_provider import LLMProvider, Message, LLMConfig
import re


@dataclass
class AmbiguityResult:
    """Result of ambiguity detection."""
    is_ambiguous: bool
    ambiguity_type: Optional[str] = None  # "pronoun", "vague", "contradictory", "multiple_interpretations", "missing_context"
    ambiguous_phrases: List[str] = None
    possible_interpretations: List[str] = None
    context_needed: Optional[str] = None
    clarification_question: Optional[str] = None


class AmbiguityDetectionService:
    """Service for detecting and handling ambiguous user inputs."""
    
    # Patterns for ambiguous language
    AMBIGUOUS_PRONOUNS = [
        r'\b(?:that|this|one|it|them|those|these)\b',
        r'\b(?:the|a)\s+one\b',
        r'\b(?:which|what|who)\s+(?:one|policy|option)\b'
    ]
    
    VAGUE_PHRASES = [
        r'\btell\s+me\s+more\b',
        r'\bwhat\s+about\s+(?:that|this|it)\b',
        r'\b(?:more|else)\s+(?:information|details|about)\b',
        r'\b(?:explain|describe|tell)\s+(?:more|about|it)\b',
        r'\b(?:can\s+you\s+)?(?:elaborate|expand)\b'
    ]
    
    CONTRADICTORY_INDICATORS = [
        r'\b(?:but|however|although|though)\b',
        r'\b(?:on\s+the\s+other\s+hand|conversely)\b',
        r'\b(?:actually|wait|hang\s+on)\b'
    ]
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider
    
    def detect_ambiguous_pronouns(self, message: str) -> Tuple[bool, List[str]]:
        """Detect ambiguous pronouns in message."""
        ambiguous_phrases = []
        message_lower = message.lower()
        
        for pattern in self.AMBIGUOUS_PRONOUNS:
            matches = re.finditer(pattern, message_lower, re.IGNORECASE)
            for match in matches:
                phrase = message[match.start():match.end()]
                ambiguous_phrases.append(phrase)
        
        return len(ambiguous_phrases) > 0, ambiguous_phrases
    
    def detect_vague_language(self, message: str) -> Tuple[bool, List[str]]:
        """Detect vague language in message."""
        vague_phrases = []
        message_lower = message.lower()
        
        for pattern in self.VAGUE_PHRASES:
            matches = re.finditer(pattern, message_lower, re.IGNORECASE)
            for match in matches:
                phrase = message[match.start():match.end()]
                vague_phrases.append(phrase)
        
        return len(vague_phrases) > 0, vague_phrases
    
    def detect_contradictory_statements(self, message: str, recent_messages: List[str]) -> bool:
        """Detect contradictory statements by comparing with recent messages."""
        message_lower = message.lower()
        
        # Check for contradictory indicators
        has_contradiction_indicator = any(
            re.search(pattern, message_lower, re.IGNORECASE)
            for pattern in self.CONTRADICTORY_INDICATORS
        )
        
        if not has_contradiction_indicator:
            return False
        
        # Check if message contradicts recent statements
        # Simple heuristic: if recent messages contain positive sentiment and current has negative (or vice versa)
        if recent_messages:
            # This is a simple heuristic - could be enhanced with sentiment analysis
            recent_text = " ".join(recent_messages[-3:]).lower()
            negative_words = ["no", "not", "don't", "won't", "can't", "shouldn't", "never", "none"]
            positive_words = ["yes", "interested", "want", "need", "like", "good", "great"]
            
            recent_negative = any(word in recent_text for word in negative_words)
            recent_positive = any(word in recent_text for word in positive_words)
            current_negative = any(word in message_lower for word in negative_words)
            current_positive = any(word in message_lower for word in positive_words)
            
            if (recent_negative and current_positive) or (recent_positive and current_negative):
                return True
        
        return False
    
    async def detect_ambiguity(
        self,
        message: str,
        context: Dict[str, Any],
        recent_messages: Optional[List[str]] = None
    ) -> AmbiguityResult:
        """
        Detect ambiguity in user message.
        
        Args:
            message: User message to analyze
            context: Conversation context (stage, interest level, recent topics, etc.)
            recent_messages: Recent conversation messages for contradiction detection
        
        Returns:
            AmbiguityResult with detection results
        """
        if recent_messages is None:
            recent_messages = []
        
        # Check for ambiguous pronouns
        has_pronouns, ambiguous_phrases = self.detect_ambiguous_pronouns(message)
        
        # Check for vague language
        has_vague, vague_phrases = self.detect_vague_language(message)
        
        # Check for contradictory statements
        has_contradiction = self.detect_contradictory_statements(message, recent_messages)
        
        # Use LLM to detect multiple interpretations if available
        has_multiple_interpretations = False
        possible_interpretations = []
        context_needed = None
        
        if self.llm_provider and (has_pronouns or has_vague or len(message.strip()) < 10):
            try:
                # Ask LLM to analyze ambiguity
                from app.src.llm.providers.llm_provider import LLMConfig
                analysis_prompt = f"""Analyze this message for ambiguity in the context of a life insurance sales conversation:

Message: "{message}"

Context:
- Conversation stage: {context.get('conversation_stage', 'unknown')}
- Recent topics: {context.get('recent_topics', 'none')}
- Policies discussed: {context.get('policies_discussed', 'none')}

Does this message have multiple possible interpretations? If yes, list 2-3 possible meanings. If not, respond with "none".

Respond in this format:
AMBIGUITY: yes/no
MEANINGS: [list of possible meanings, or "none"]
CONTEXT_NEEDED: [what context is missing, or "none"]"""
                
                response = await self.llm_provider.generate_response(
                    [Message(role="user", content=analysis_prompt)],
                    config=LLMConfig(temperature=0.3, max_tokens=200)
                )
                
                response_text = response.content.lower()
                
                # Parse LLM response
                if "ambiguity: yes" in response_text or "has multiple" in response_text:
                    has_multiple_interpretations = True
                    
                    # Extract meanings
                    if "meanings:" in response_text:
                        meanings_section = response_text.split("meanings:")[1].split("context_needed:")[0].strip()
                        meanings = [m.strip("- ").strip() for m in meanings_section.split("\n") if m.strip() and m.strip() != "none"]
                        possible_interpretations = [m for m in meanings if m and "none" not in m.lower()][:3]
                    
                    # Extract context needed
                    if "context_needed:" in response_text:
                        context_section = response_text.split("context_needed:")[1].strip()
                        context_needed = context_section.split("\n")[0].strip()
                        if "none" in context_needed.lower():
                            context_needed = None
            except Exception:
                # If LLM fails, fall back to pattern-based detection
                pass
        
        # Determine ambiguity type and result
        is_ambiguous = has_pronouns or has_vague or has_contradiction or has_multiple_interpretations
        
        if not is_ambiguous:
            return AmbiguityResult(is_ambiguous=False)
        
        # Determine primary ambiguity type
        ambiguity_type = None
        if has_pronouns:
            ambiguity_type = "pronoun"
        elif has_vague:
            ambiguity_type = "vague"
        elif has_contradiction:
            ambiguity_type = "contradictory"
        elif has_multiple_interpretations:
            ambiguity_type = "multiple_interpretations"
        else:
            ambiguity_type = "missing_context"
        
        return AmbiguityResult(
            is_ambiguous=True,
            ambiguity_type=ambiguity_type,
            ambiguous_phrases=(ambiguous_phrases + vague_phrases) if (has_pronouns or has_vague) else [],
            possible_interpretations=possible_interpretations if possible_interpretations else None,
            context_needed=context_needed
        )
    
    async def generate_clarification_request(
        self,
        ambiguity_result: AmbiguityResult,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate a helpful clarification request based on ambiguity detection.
        
        Args:
            ambiguity_result: Result from ambiguity detection
            message: Original ambiguous message
            context: Conversation context
        
        Returns:
            Clarification question string
        """
        if not ambiguity_result.is_ambiguous:
            return ""
        
        # Build context information for clarification
        context_info = []
        
        recent_topics = context.get("recent_topics", [])
        policies_discussed = context.get("policies_discussed", [])
        conversation_stage = context.get("conversation_stage", "")
        
        if policies_discussed:
            if isinstance(policies_discussed, list):
                policy_list = ", ".join(policies_discussed[:3])
            else:
                policy_list = str(policies_discussed)
            context_info.append(f"Policies we discussed: {policy_list}")
        
        if recent_topics:
            if isinstance(recent_topics, list):
                topics = ", ".join(recent_topics[:2])
            else:
                topics = str(recent_topics)
            context_info.append(f"Recent topics: {topics}")
        
        context_text = " ".join(context_info) if context_info else ""
        
        # Generate clarification based on ambiguity type
        if ambiguity_result.ambiguity_type == "pronoun":
            if policies_discussed:
                if isinstance(policies_discussed, list):
                    policy_options = ", ".join([f"{p}" for p in policies_discussed[:3]])
                else:
                    policy_options = str(policies_discussed)
                clarification = f"I'd be happy to help! Which policy are you referring to? We discussed {policy_options}."
            elif context_text:
                clarification = f"I want to make sure I understand. {context_text} Could you please clarify what specifically you're referring to?"
            else:
                clarification = "I'd be happy to help! Could you please clarify what you're referring to? For example, are you asking about a specific policy, coverage details, or something else?"
        
        elif ambiguity_result.ambiguity_type == "vague":
            if context_text:
                clarification = f"Of course! {context_text} Would you like more details about what we just discussed, or something else?"
            elif policies_discussed:
                clarification = "I'd be happy to provide more information! Would you like more details about the policy we just discussed, or something else?"
            else:
                clarification = "I'd be happy to provide more information! What specifically would you like to know more about?"
        
        elif ambiguity_result.ambiguity_type == "contradictory":
            clarification = "I understand you might have mixed feelings about this. Could you help me understand what concerns you most about life insurance, and what aspects might interest you?"
        
        elif ambiguity_result.ambiguity_type == "multiple_interpretations":
            if ambiguity_result.possible_interpretations:
                interpretations_text = "\n".join([f"- {i}" for i in ambiguity_result.possible_interpretations[:3]])
                clarification = f"I want to make sure I understand correctly. Are you asking about:\n{interpretations_text}\n\nPlease let me know which one, or clarify what you mean."
            else:
                clarification = "I want to make sure I understand correctly. Could you please clarify what you mean?"
        
        else:  # missing_context
            if ambiguity_result.context_needed:
                clarification = f"To help you better, I need a bit more information: {ambiguity_result.context_needed}"
            else:
                clarification = "I want to make sure I understand correctly. Could you please provide a bit more detail?"
        
        # Use LLM to refine clarification if available
        if self.llm_provider:
            try:
                refinement_prompt = f"""Make this clarification request more natural and helpful. Keep it friendly and concise:

Original: "{clarification}"

Context:
- User message: "{message}"
- Conversation stage: {conversation_stage}

Generate a natural, helpful clarification question (max 2 sentences):"""
                
                response = await self.llm_provider.generate_response(
                    [Message(role="user", content=refinement_prompt)],
                    config=LLMConfig(temperature=0.7, max_tokens=150)
                )
                
                refined = response.content.strip()
                if refined and len(refined) > 10:
                    clarification = refined
            except Exception:
                pass  # Use original clarification if LLM fails
        
        return clarification

