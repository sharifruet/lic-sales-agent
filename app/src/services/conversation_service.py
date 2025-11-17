"""Conversation Service following TDD specification."""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.providers.llm_provider import LLMProvider, LLMConfig, Message, Intent
from src.llm.context_manager import ContextManager
from src.llm.prompt_manager import PromptManager
from src.llm.response_filter import ResponseFilter
from src.llm.stage_configs import get_stage_config
from src.models.message import Message as MessageModel
from src.models.conversation import Conversation
from src.services.session_manager import (
    ConversationStage,
    InterestLevel,
    SessionManager,
    SessionState,
)
from src.services.policy_service import PolicyService
from src.services.validation_service import ValidationService
from src.services.lead_service import LeadService
from src.services.information_extraction_service import InformationExtractionService
from src.middleware.error_handler import SessionNotFoundError


@dataclass
class ConversationResponse:
    """Response from conversation processing."""
    message: str
    session_id: str
    conversation_id: str
    interest_detected: InterestLevel
    conversation_stage: ConversationStage
    metadata: Dict[str, Any] = None


class ConversationService:
    """Conversation orchestration following TDD specification."""

    def __init__(
        self,
        db: AsyncSession,
        llm_provider: Optional[LLMProvider] = None,
        session_manager: Optional[SessionManager] = None,
        policy_service: Optional[PolicyService] = None,
        validation_service: Optional[ValidationService] = None,
        lead_service: Optional[LeadService] = None,
    ):
        self.db = db
        self.llm_provider = llm_provider
        self.session_manager = session_manager or SessionManager()
        self.policy_service = policy_service
        self.validation_service = validation_service
        self.lead_service = lead_service
        self.context_manager = ContextManager()
        self.prompt_manager = PromptManager()
        self.response_filter = ResponseFilter()
        self.info_extraction = InformationExtractionService(llm_provider) if llm_provider else None

    async def start_conversation(self) -> ConversationResponse:
        """Initialize new conversation session."""
        import uuid
        
        session_id = uuid.uuid4().hex
        conversation_id = uuid.uuid4().hex
        
        # Create conversation in database
        conv = Conversation(
            session_id=session_id,
            stage=ConversationStage.INTRODUCTION.value,
            created_at=datetime.utcnow(),
        )
        self.db.add(conv)
        await self.db.flush()
        
        # Create session state
        state = await self.session_manager.create_session(session_id, conv.id)
        
        # Generate welcome message
        welcome_message = await self._get_welcome_message(state)
        
        # Save welcome message
        self.db.add(MessageModel(
            conversation_id=conv.id,
            role="assistant",
            content=welcome_message
        ))
        await self.db.flush()
        
        return ConversationResponse(
            message=welcome_message,
            session_id=session_id,
            conversation_id=str(conv.id),
            interest_detected=InterestLevel.NONE,
            conversation_stage=ConversationStage.INTRODUCTION,
            metadata={"message_count": 1}
        )

    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> ConversationResponse:
        """Process user message following TDD algorithm."""
        # 1. Load session and context
        state = await self.session_manager.get_session(session_id)
        if not state:
            conv_id = await self._get_conversation_id(session_id)
            if not conv_id:
                raise SessionNotFoundError(session_id)
            state = await self.session_manager.create_session(session_id, conv_id)
        
        conv_id = await self._get_conversation_id(session_id)
        
        # 2. Validate and sanitize input
        if self.info_extraction:
            sanitized_message = self.info_extraction.sanitize_input(user_message)
        else:
            sanitized_message = user_message.strip()
        
        # 3. Save user message to conversation log
        self.db.add(MessageModel(
            conversation_id=conv_id,
            role="user",
            content=sanitized_message
        ))
        await self.db.flush()
        
        # 4. Detect intent (using TDD specification method)
        context_dict = {
            "conversation_stage": state.conversation_stage.value if hasattr(state.conversation_stage, 'value') else str(state.conversation_stage),
            "interest_level": state.interest_level.value if hasattr(state.interest_level, 'value') else str(state.interest_level),
        }
        intent = await self.detect_intent(sanitized_message, context_dict)
        
        # 5. Check for exit signals
        if self._is_exit_signal(sanitized_message, intent):
            return await self._handle_exit(session_id, state)
        
        # 6. Update customer profile if new information
        extracted_data = {}
        if self.info_extraction:
            extracted_data = await self.info_extraction.extract_information(
                sanitized_message,
                {"conversation_stage": state.conversation_stage.value}
            )
        
        if extracted_data:
            # Update customer profile
            if extracted_data.get("age"):
                state.customer_profile.age = extracted_data["age"]
            if extracted_data.get("name"):
                state.customer_profile.name = extracted_data["name"]
            if extracted_data.get("phone"):
                state.customer_profile.phone = extracted_data["phone"]
            if extracted_data.get("email"):
                state.customer_profile.email = extracted_data["email"]
            if extracted_data.get("address"):
                state.customer_profile.address = extracted_data["address"]
            
            # Also update collected_data if applicable
            if extracted_data.get("name"):
                state.collected_data.full_name = extracted_data["name"]
            if extracted_data.get("phone"):
                state.collected_data.phone_number = extracted_data["phone"]
            if extracted_data.get("email"):
                state.collected_data.email = extracted_data["email"]
            if extracted_data.get("address"):
                state.collected_data.address = extracted_data["address"]
            
            await self.session_manager.save_session(state)
        
        # 7. Check conversation stage and handle accordingly
        stage = self._determine_stage(state, intent)
        
        if stage == ConversationStage.INFORMATION_COLLECTION:
            return await self._handle_information_collection(state, sanitized_message, conv_id)
        elif stage == ConversationStage.OBJECTION_HANDLING:
            return await self._handle_objection(state, sanitized_message, conv_id)
        
        # 8. Build context for LLM
        customer_profile_dict = {
            "age": state.customer_profile.age,
            "name": state.customer_profile.name,
            "purpose": state.customer_profile.purpose,
            "dependents": state.customer_profile.dependents,
            "coverage_amount_interest": state.customer_profile.coverage_amount_interest,
            "phone": state.customer_profile.phone,
            "email": state.customer_profile.email,
            "address": state.customer_profile.address,
        }
        
        # Get relevant policies
        policies = []
        if self.policy_service:
            try:
                policy_list = await self.policy_service.list_policies()
                policies = [
                    {
                        "name": p.name,
                        "coverage_amount": p.coverage_amount,
                        "monthly_premium": float(p.monthly_premium),
                        "term_years": p.term_years,
                    }
                    for p in policy_list[:5]
                ]
            except Exception:
                pass
        
        # Get message history from database
        message_history = await self._get_message_history_for_context(conv_id)
        
        context = self.context_manager.build_context(
            state,
            customer_profile_dict,
            policies,
            message_history=message_history
        )
        
        # 9. Generate response using LLM
        if self.llm_provider:
            # Build system prompt
            system_prompt = self.prompt_manager.build_system_prompt(
                stage,
                customer_profile_dict,
                policies
            )
            
            # Add system prompt to messages
            llm_messages = [Message(role="system", content=system_prompt)] + context.messages
            
            # Add current user message
            llm_messages.append(Message(role="user", content=sanitized_message))
            
            # Use stage-specific configuration
            stage_config = get_stage_config(stage)
            
            llm_response = await self.llm_provider.generate_response(
                llm_messages,
                config=stage_config
            )
            llm_content = llm_response.content
        else:
            # Fallback response
            llm_content = f"I understand you said: {sanitized_message}. How can I help you with life insurance?"
        
        # 10. Filter and process response
        filtered_response = self.response_filter.filter_response(llm_content)
        
        # 11. Detect interest in response
        interest_level = self._detect_interest_from_response(filtered_response, state)
        state.interest_level = interest_level
        
        # 12. Save assistant message
        self.db.add(MessageModel(
            conversation_id=conv_id,
            role="assistant",
            content=filtered_response
        ))
        await self.db.flush()
        
        # 13. Update session state
        from datetime import timezone
        state.last_activity = datetime.now(timezone.utc)
        state.message_count += 1
        state.conversation_stage = stage
        await self.session_manager.save_session(state)
        
        # Update conversation in DB
        conv = await self._get_conversation(session_id)
        conv.stage = stage.value
        conv.message_count = state.message_count
        await self.db.flush()
        
        # 14. Return response
        return ConversationResponse(
            message=filtered_response,
            session_id=session_id,
            conversation_id=str(conv_id),
            interest_detected=interest_level,
            conversation_stage=stage,
            metadata={
                "message_count": state.message_count,
                "extracted_data": extracted_data
            }
        )

    async def end_conversation(
        self,
        session_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gracefully end conversation."""
        state = await self.session_manager.get_session(session_id)
        if not state:
            raise SessionNotFoundError(session_id)
        
        # Generate summary
        summary = await self.generate_summary(session_id)
        
        # Update conversation
        conv = await self._get_conversation(session_id)
        conv.stage = ConversationStage.ENDED.value
        
        # Update session
        state.conversation_stage = ConversationStage.ENDED
        await self.session_manager.save_session(state)
        
        return {
            "session_id": session_id,
            "conversation_id": str(conv.id),
            "status": "ended",
            "summary": summary,
            "duration_seconds": int((datetime.now(timezone.utc) - state.created_at).total_seconds()) if state.created_at else 0
        }

    async def generate_summary(self, session_id: str) -> str:
        """Generate conversation summary."""
        conv = await self._get_conversation(session_id)
        messages = await self._get_messages(conv.id, limit=50)
        
        # Build summary prompt
        lines = []
        for m in messages:
            prefix = "Customer" if m.role == "user" else "Agent"
            lines.append(f"{prefix}: {m.content}")
        transcript = "\n".join(lines)
        
        summary_prompt = (
            "Summarize this life insurance sales conversation in 2-3 sentences, "
            "covering customer's needs, policies discussed, interest level, and outcome.\n\n"
            f"{transcript}"
        )
        
        if self.llm_provider:
            try:
                response = await self.llm_provider.generate_response(
                    [Message(role="user", content=summary_prompt)],
                    config=LLMConfig(temperature=0.3, max_tokens=200)
                )
                return response.content
            except Exception:
                pass
        
        return "Conversation completed."

    def _is_exit_signal(self, message: str, intent: Intent) -> bool:
        """Detect if message indicates customer wants to exit."""
        exit_keywords = [
            "not interested", "no thanks", "i'll pass",
            "i don't want", "maybe later", "i have to go",
            "thanks but no", "not for me"
        ]
        
        message_lower = message.lower()
        
        # Explicit exit keywords
        for keyword in exit_keywords:
            if keyword in message_lower:
                return True
        
        # Intent-based detection
        if intent == Intent.EXIT:
            return True
        
        return False

    async def _handle_exit(self, session_id: str, state: SessionState) -> ConversationResponse:
        """Handle exit signal."""
        exit_message = "Thank you for your time. Feel free to reach out if you have questions in the future."
        
        conv_id = await self._get_conversation_id(session_id)
        self.db.add(MessageModel(
            conversation_id=conv_id,
            role="assistant",
            content=exit_message
        ))
        await self.db.flush()
        
        # End conversation
        await self.end_conversation(session_id, reason="customer_requested")
        
        return ConversationResponse(
            message=exit_message,
            session_id=session_id,
            conversation_id=str(conv_id),
            interest_detected=InterestLevel.NONE,
            conversation_stage=ConversationStage.ENDED
        )

    async def _handle_information_collection(
        self,
        state: SessionState,
        message: str,
        conv_id: int
    ) -> ConversationResponse:
        """Handle information collection stage."""
        # Use LLM to guide information collection
        prompt = f"""You are collecting customer information for a life insurance application.
Current collected data: {state.collected_data}
Customer just said: {message}

Ask for the next missing piece of information in a friendly way."""
        
        if self.llm_provider:
            response = await self.llm_provider.generate_response(
                [Message(role="user", content=prompt)],
                config=LLMConfig(temperature=0.7, max_tokens=150)
            )
            reply = response.content
        else:
            reply = "I'd like to collect some information from you. Could you please provide your full name?"
        
        filtered_reply = self.response_filter.filter_response(reply)
        
        self.db.add(MessageModel(
            conversation_id=conv_id,
            role="assistant",
            content=filtered_reply
        ))
        await self.db.flush()
        
        return ConversationResponse(
            message=filtered_reply,
            session_id=state.session_id,
            conversation_id=str(conv_id),
            interest_detected=state.interest_level,
            conversation_stage=ConversationStage.INFORMATION_COLLECTION
        )

    async def _handle_objection(
        self,
        state: SessionState,
        message: str,
        conv_id: int
    ) -> ConversationResponse:
        """Handle objection using templates from PromptManager."""
        # Detect objection type
        objection_type = self._detect_objection_type(message)
        
        # Get context for objection response
        context = {
            "age": state.customer_profile.age or "your current",
            "coverage_amount": 500000,  # Default, could be from profile
            "monthly_premium": 50,  # Default, could be from policy
            "min_coverage": 100000,
        }
        
        # Try to use template first, fallback to LLM if needed
        if objection_type and objection_type in ["cost", "necessity", "complexity", "trust", "timing", "comparison"]:
            reply = self.prompt_manager.get_objection_response(objection_type, context)
        else:
            # Use LLM for custom objections
            prompt = f"""A customer raised an objection: {message}
Customer profile: {state.customer_profile}

Respond empathetically, address their concern with facts, and try to overcome the objection naturally."""
            
            if self.llm_provider:
                response = await self.llm_provider.generate_response(
                    [Message(role="user", content=prompt)],
                    config=get_stage_config(ConversationStage.OBJECTION_HANDLING)
                )
                reply = response.content
            else:
                reply = "I understand your concern. Let me address that..."
        
        filtered_reply = self.response_filter.filter_response(reply)
        
        self.db.add(MessageModel(
            conversation_id=conv_id,
            role="assistant",
            content=filtered_reply
        ))
        await self.db.flush()
        
        return ConversationResponse(
            message=filtered_reply,
            session_id=state.session_id,
            conversation_id=str(conv_id),
            interest_detected=state.interest_level,
            conversation_stage=ConversationStage.OBJECTION_HANDLING
        )

    def _determine_stage(self, state: SessionState, intent: Intent) -> ConversationStage:
        """Determine current conversation stage."""
        if state.conversation_stage == ConversationStage.ENDED:
            return ConversationStage.ENDED
        
        # Check if information collection is ready
        if state.interest_level in [InterestLevel.HIGH, InterestLevel.MEDIUM]:
            if not state.collected_data.is_complete():
                return ConversationStage.INFORMATION_COLLECTION
        
        # Check for objections
        if intent == Intent.OBJECTION:
            return ConversationStage.OBJECTION_HANDLING
        
        # Check profile completeness for qualification
        if state.conversation_stage == ConversationStage.INTRODUCTION:
            if self._is_profile_complete(state.customer_profile):
                return ConversationStage.INFORMATION
            return ConversationStage.QUALIFICATION
        
        # Default progression
        return state.conversation_stage

    def _is_profile_complete(self, profile) -> bool:
        """Check if customer profile is complete enough."""
        return bool(profile.age and profile.purpose)

    async def detect_intent(self, message: str, context: Dict) -> Intent:
        """Analyze customer intent from message (TDD specification method)."""
        if self.llm_provider:
            # Use LLM for intent classification
            try:
                return await self.llm_provider.classify_intent(message)
            except Exception:
                pass
        
        # Fallback to keyword-based detection
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ["hello", "hi", "hey", "greetings"]):
            return Intent.GREETING
        elif any(kw in message_lower for kw in ["not interested", "no thanks", "no", "stop"]):
            return Intent.EXIT
        elif any(kw in message_lower for kw in ["expensive", "cost", "too much", "afford"]):
            return Intent.OBJECTION
        elif any(kw in message_lower for kw in ["interested", "want", "apply", "sign up"]):
            return Intent.INTEREST
        elif "?" in message:
            return Intent.QUESTION
        else:
            return Intent.UNKNOWN
    
    def detect_interest(self, state: SessionState) -> InterestLevel:
        """Detect buying interest signals from conversation state (TDD specification method)."""
        # Use existing interest level if already set
        if state.interest_level != InterestLevel.NONE:
            return state.interest_level
        
        # Analyze based on conversation state
        score = 0
        
        # Check if customer has selected a policy
        if state.collected_data.policy_of_interest:
            score += 5
        
        # Check if information collection has started
        if state.collected_data.full_name or state.collected_data.phone_number:
            score += 3
        
        # Check conversation stage
        if state.conversation_stage == ConversationStage.INFORMATION_COLLECTION:
            score += 2
        elif state.conversation_stage == ConversationStage.CLOSING:
            score += 5
        
        # Determine level
        if score >= 8:
            return InterestLevel.HIGH
        elif score >= 5:
            return InterestLevel.MEDIUM
        elif score >= 2:
            return InterestLevel.LOW
        else:
            return InterestLevel.NONE
    
    def _detect_interest_from_response(self, response: str, state: SessionState) -> InterestLevel:
        """Detect interest level from conversation state."""
        # Use existing interest level, or detect from keywords
        if state.interest_level != InterestLevel.NONE:
            return state.interest_level
        
        response_lower = response.lower()
        positive_keywords = ["interested", "want", "apply", "sign up", "next step"]
        
        for keyword in positive_keywords:
            if keyword in response_lower:
                return InterestLevel.MEDIUM
        
        return InterestLevel.NONE
    
    def _detect_objection_type(self, message: str) -> Optional[str]:
        """Detect type of objection from message."""
        message_lower = message.lower()
        
        # Cost objections
        if any(kw in message_lower for kw in ["expensive", "cost", "price", "afford", "cheap", "too much"]):
            return "cost"
        
        # Necessity objections
        if any(kw in message_lower for kw in ["don't need", "not necessary", "don't want", "not for me"]):
            return "necessity"
        
        # Complexity objections
        if any(kw in message_lower for kw in ["complicated", "confusing", "complex", "don't understand", "too hard"]):
            return "complexity"
        
        # Trust objections
        if any(kw in message_lower for kw in ["trust", "scam", "legit", "real", "believe", "skeptical"]):
            return "trust"
        
        # Timing objections
        if any(kw in message_lower for kw in ["later", "think about it", "not now", "maybe later", "wait"]):
            return "timing"
        
        # Comparison objections
        if any(kw in message_lower for kw in ["other company", "competitor", "better deal", "cheaper elsewhere"]):
            return "comparison"
        
        return None

    async def _get_welcome_message(self, state: SessionState) -> str:
        """Get welcome message using PromptManager templates."""
        return self.prompt_manager.get_welcome_message()

    async def _get_conversation_id(self, session_id: str) -> int:
        """Get conversation ID from session ID."""
        res = await self.db.execute(
            select(Conversation.id).where(Conversation.session_id == session_id)
        )
        row = res.first()
        if not row:
            raise ValueError("Invalid session_id")
        return row[0]

    async def _get_conversation(self, session_id: str) -> Conversation:
        """Get conversation from session ID."""
        res = await self.db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conv = res.scalar_one_or_none()
        if not conv:
            raise ValueError("Invalid session_id")
        return conv

    async def _get_messages(self, conversation_id: int, limit: int = 50):
        """Get messages for conversation."""
        res = await self.db.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
            .limit(limit)
        )
        return res.scalars().all()
    
    async def _get_message_history_for_context(self, conversation_id: int) -> List[Dict]:
        """Get message history formatted for context manager."""
        messages = await self._get_messages(conversation_id, limit=50)
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
