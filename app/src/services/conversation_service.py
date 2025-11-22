"""Conversation Service following TDD specification."""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

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
from src.services.ambiguity_detection_service import AmbiguityDetectionService
from src.services.retry_service import RetryService, RetryConfig
from src.services.fallback_service import FallbackService
from src.middleware.error_handler import SessionNotFoundError, LLMAPIError


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
        self.ambiguity_detection = AmbiguityDetectionService(llm_provider) if llm_provider else None
        self.retry_service = RetryService(RetryConfig(max_attempts=3, initial_delay=1.0, max_delay=10.0))
        self.fallback_service = FallbackService()
        self.fallback_service = FallbackService()

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
        
        # 4. Detect ambiguity (US-021: Handle Ambiguous Inputs)
        # Get recent messages for context
        recent_messages = await self._get_recent_messages(conv_id, limit=5)
        recent_message_texts = [msg.get("content", "") for msg in recent_messages if msg.get("role") == "user"]
        
        # Get policies discussed from context
        policies_discussed = []
        if self.policy_service:
            try:
                all_policies = await self.policy_service.list_policies()
                # Extract policy names mentioned in recent messages
                for msg in recent_messages:
                    if msg.get("role") == "assistant":
                        content = msg.get("content", "").lower()
                        for policy in all_policies[:5]:  # Check top 5 policies
                            if policy.name.lower() in content:
                                policies_discussed.append(policy.name)
                policies_discussed = list(set(policies_discussed))  # Remove duplicates
            except Exception:
                pass
        
        # Detect ambiguity
        ambiguity_result = None
        if self.ambiguity_detection:
            context_for_ambiguity = {
                "conversation_stage": state.conversation_stage.value if hasattr(state.conversation_stage, 'value') else str(state.conversation_stage),
                "interest_level": state.interest_level.value if hasattr(state.interest_level, 'value') else str(state.interest_level),
                "recent_topics": self._extract_recent_topics(recent_messages),
                "policies_discussed": policies_discussed[:3] if policies_discussed else [],
            }
            
            ambiguity_result = await self.ambiguity_detection.detect_ambiguity(
                sanitized_message,
                context_for_ambiguity,
                recent_message_texts
            )
            
            # If ambiguous and context cannot resolve it, generate clarification request
            if ambiguity_result.is_ambiguous:
                # Try to resolve using context first
                can_resolve_with_context = self._can_resolve_ambiguity_with_context(
                    ambiguity_result,
                    context_for_ambiguity,
                    recent_messages
                )
                
                if not can_resolve_with_context:
                    # Generate clarification request
                    clarification = await self.ambiguity_detection.generate_clarification_request(
                        ambiguity_result,
                        sanitized_message,
                        context_for_ambiguity
                    )
                    
                    if clarification:
                        # Save clarification response
                        filtered_clarification = self.response_filter.filter_response(clarification)
                        self.db.add(MessageModel(
                            conversation_id=conv_id,
                            role="assistant",
                            content=filtered_clarification
                        ))
                        await self.db.flush()
                        
                        # Return clarification response
                        return ConversationResponse(
                            message=filtered_clarification,
                            session_id=state.session_id,
                            conversation_id=str(conv_id),
                            interest_detected=state.interest_level,
                            conversation_stage=state.conversation_stage,
                            metadata={
                                "ambiguity_detected": True,
                                "ambiguity_type": ambiguity_result.ambiguity_type,
                                "possible_interpretations": ambiguity_result.possible_interpretations,
                            }
                        )
        
        # 5. Detect intent (using TDD specification method)
        context_dict = {
            "conversation_stage": state.conversation_stage.value if hasattr(state.conversation_stage, 'value') else str(state.conversation_stage),
            "interest_level": state.interest_level.value if hasattr(state.interest_level, 'value') else str(state.interest_level),
        }
        intent = await self.detect_intent(sanitized_message, context_dict)
        
        # 6. Check for exit signals
        if self._is_exit_signal(sanitized_message, intent):
            return await self._handle_exit(session_id, state)
        
        # 7. Update customer profile if new information
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
        
        # 8. Check conversation stage and handle accordingly
        stage = self._determine_stage(state, intent)
        
        if stage == ConversationStage.INFORMATION_COLLECTION:
            return await self._handle_information_collection(state, sanitized_message, conv_id)
        elif stage == ConversationStage.OBJECTION_HANDLING:
            return await self._handle_objection(state, sanitized_message, conv_id)
        
        # 9. Build context for LLM
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
        
        # 9. Generate response using LLM with retry and fallback (US-022)
        llm_content = None
        if self.llm_provider:
            try:
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
                
                # Retry LLM call with exponential backoff (AC-022.3, AC-022.7)
                async def _generate_llm_response():
                    return await self.llm_provider.generate_response(
                        llm_messages,
                        config=stage_config
                    )
                
                try:
                    llm_response = await self.retry_service.retry_with_backoff(
                        _generate_llm_response,
                        operation_name="LLM response generation",
                        retryable_exceptions=[Exception],
                        non_retryable_exceptions=[]  # Retry all LLM errors
                    )
                    llm_content = llm_response.content
                except Exception as e:
                    # Log LLM error but don't raise - use fallback instead (AC-022.3)
                    logger.error(f"LLM service failed after retries: {type(e).__name__}: {str(e)}")
                    llm_content = None
            except Exception as e:
                # Log error
                logger.error(f"LLM call error: {type(e).__name__}: {str(e)}")
                llm_content = None
        
        # Use fallback response if LLM failed (AC-022.3: Fallback responses)
        if not llm_content:
            # Detect intent for better fallback (simple keyword-based if LLM not available)
            intent_keyword = None
            message_lower = sanitized_message.lower()
            if any(word in message_lower for word in ["hello", "hi", "hey"]):
                intent_keyword = "greeting"
            elif any(word in message_lower for word in ["interested", "want", "need", "looking"]):
                intent_keyword = "interest"
            elif any(word in message_lower for word in ["?", "what", "how", "tell me"]):
                intent_keyword = "question"
            
            llm_content = self.fallback_service.get_fallback_response(
                stage=stage,
                intent=intent_keyword,
                interest_level=state.interest_level,
                error_type="llm_service_error"
            )
        
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
                # Retry LLM call with exponential backoff (AC-022.3)
                async def _generate_summary():
                    return await self.llm_provider.generate_response(
                        [Message(role="user", content=summary_prompt)],
                        config=LLMConfig(temperature=0.3, max_tokens=200)
                    )
                
                try:
                    response = await self.retry_service.retry_with_backoff(
                        _generate_summary,
                        operation_name="LLM summary generation",
                        retryable_exceptions=[Exception],
                        non_retryable_exceptions=[]  # Retry all LLM errors
                    )
                    return response.content
                except Exception as e:
                    logger.error(f"LLM summary generation failed after retries: {type(e).__name__}: {str(e)}")
                    # Fall through to fallback
            except Exception as e:
                logger.error(f"LLM summary call error: {type(e).__name__}: {str(e)}")
        
        # Fallback summary
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
        """Handle information collection stage with confirmation step."""
        # Check if we're waiting for confirmation
        if state.awaiting_confirmation:
            return await self._handle_confirmation_response(state, message, conv_id)
        
        # Check if all mandatory fields are collected
        if state.collected_data.is_complete() and not state.awaiting_confirmation:
            # Generate and present summary, request confirmation
            summary = self._generate_information_summary(state)
            state.awaiting_confirmation = True
            state.confirmation_attempts = 1
            await self.session_manager.save_session(state)
            
            filtered_reply = self.response_filter.filter_response(summary)
            
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
        
        # Continue collecting information
        # Use LLM to guide information collection
        missing_fields = self._get_missing_fields(state.collected_data)
        prompt = f"""You are collecting customer information for a life insurance application.
Current collected data: {state.collected_data}
Missing information: {missing_fields}
Customer just said: {message}

Ask for the next missing piece of information in a friendly way."""
        
        if self.llm_provider:
            try:
                # Retry LLM call with exponential backoff (AC-022.3)
                async def _generate_info_request():
                    return await self.llm_provider.generate_response(
                        [Message(role="user", content=prompt)],
                        config=LLMConfig(temperature=0.7, max_tokens=150)
                    )
                
                try:
                    response = await self.retry_service.retry_with_backoff(
                        _generate_info_request,
                        operation_name="LLM information request generation",
                        retryable_exceptions=[Exception],
                        non_retryable_exceptions=[]
                    )
                    reply = response.content
                except Exception as e:
                    logger.error(f"LLM info request generation failed after retries: {type(e).__name__}: {str(e)}")
                    # Fall through to fallback
                    reply = None
            except Exception as e:
                logger.error(f"LLM info request call error: {type(e).__name__}: {str(e)}")
                reply = None
        else:
            reply = None
        
        if not reply:
            # Fallback to asking for next missing field
            if not state.collected_data.full_name:
                reply = "Could you please provide your full name?"
            elif not state.collected_data.phone_number:
                reply = "Could you please provide your phone number?"
            elif not state.collected_data.nid:
                reply = "Could you please provide your National ID?"
            elif not state.collected_data.address:
                reply = "Could you please provide your address?"
            elif not state.collected_data.policy_of_interest:
                reply = "Which policy are you interested in?"
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

    def _generate_information_summary(self, state: SessionState) -> str:
        """Generate human-readable summary of collected information."""
        collected = state.collected_data
        summary_lines = [
            "Here's a summary of the information I've collected:",
            "",
            f"**Full Name:** {collected.full_name or 'Not provided'}",
            f"**Phone Number:** {collected.phone_number or 'Not provided'}",
            f"**National ID:** {collected.nid or 'Not provided'}",
            f"**Address:** {collected.address or 'Not provided'}",
            f"**Policy of Interest:** {collected.policy_of_interest or 'Not provided'}",
        ]
        
        if collected.email:
            summary_lines.append(f"**Email:** {collected.email}")
        if collected.preferred_contact_time:
            summary_lines.append(f"**Preferred Contact Time:** {collected.preferred_contact_time}")
        if collected.notes:
            summary_lines.append(f"**Notes:** {collected.notes}")
        
        summary_lines.append("")
        summary_lines.append("Is this information correct? Please reply 'Yes' if it's correct, or tell me what needs to be changed.")
        
        return "\n".join(summary_lines)

    def _get_missing_fields(self, collected_data) -> List[str]:
        """Get list of missing mandatory fields."""
        missing = []
        if not collected_data.full_name:
            missing.append("full name")
        if not collected_data.phone_number:
            missing.append("phone number")
        if not collected_data.nid:
            missing.append("National ID")
        if not collected_data.address:
            missing.append("address")
        if not collected_data.policy_of_interest:
            missing.append("policy of interest")
        return missing

    async def _handle_confirmation_response(
        self,
        state: SessionState,
        message: str,
        conv_id: int
    ) -> ConversationResponse:
        """Handle confirmation response (yes/no/correction)."""
        message_lower = message.lower().strip()
        
        # Detect confirmation intent
        confirmed = False
        field_to_correct = None
        
        # Check for positive confirmation
        confirmation_keywords = ["yes", "correct", "right", "that's right", "that is correct", "looks good", "ok", "okay", "confirm", "proceed"]
        if any(keyword in message_lower for keyword in confirmation_keywords):
            confirmed = True
        
        # Check for negative confirmation
        denial_keywords = ["no", "wrong", "incorrect", "that's wrong", "that is wrong", "change", "correction"]
        if any(keyword in message_lower for keyword in denial_keywords):
            confirmed = False
            # Try to extract which field needs correction
            field_to_correct = await self._extract_correction_field(message, state)
        
        # If confirmed, proceed to save
        if confirmed:
            # Reset confirmation state
            state.awaiting_confirmation = False
            state.confirmation_attempts = 0
            await self.session_manager.save_session(state)
            
            # Create lead with retry logic (AC-022.6: Database retry with backoff)
            reply = "Thank you for confirming! Your information has been saved. Our team will contact you soon."
            
            # Save lead if lead_service is available
            if self.lead_service:
                try:
                    # Retry database operation with exponential backoff
                    async def _create_lead_with_retry():
                        return await self.lead_service.create_lead(
                            name=state.collected_data.full_name,
                            phone=state.collected_data.phone_number,
                            nid=state.collected_data.nid,
                            address=state.collected_data.address,
                            interested_policy=state.collected_data.policy_of_interest,
                            email=state.collected_data.email,
                            conversation_id=conv_id,  # Link conversation to lead
                        )
                    
                    try:
                        lead = await self.retry_service.retry_with_backoff(
                            _create_lead_with_retry,
                            operation_name="Lead creation",
                            retryable_exceptions=[Exception],
                            non_retryable_exceptions=[]  # Retry database errors
                        )
                        
                        # Commit transaction with retry
                        async def _commit_transaction():
                            await self.db.commit()
                        
                        try:
                            await self.retry_service.retry_with_backoff(
                                _commit_transaction,
                                operation_name="Database commit",
                                retryable_exceptions=[Exception],
                                non_retryable_exceptions=[]
                            )
                            reply = "Thank you for confirming! Your information has been saved successfully. Our team will contact you soon."
                        except Exception as e:
                            logger.error(f"Database commit failed after retries: {type(e).__name__}: {str(e)}")
                            await self.db.rollback()
                            reply = self.fallback_service.get_database_error_message("save")
                    except Exception as e:
                        logger.error(f"Lead creation failed after retries: {type(e).__name__}: {str(e)}")
                        await self.db.rollback()
                        reply = self.fallback_service.get_database_error_message("save")
                except Exception as e:
                    logger.error(f"Lead creation error: {type(e).__name__}: {str(e)}")
                    await self.db.rollback()
                    reply = self.fallback_service.get_database_error_message("save")
            
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
                conversation_stage=ConversationStage.CLOSING
            )
        
        # Handle correction
        if field_to_correct or (not confirmed and any(kw in message_lower for kw in ["wrong", "incorrect", "change", "different"])):
            state.awaiting_confirmation = False
            state.confirmation_attempts += 1
            
            # Try to extract corrected value from the message itself
            corrected_value = None
            if field_to_correct and self.info_extraction:
                # Extract information from message to see if correction is included
                extracted = await self.info_extraction.extract_information(
                    message,
                    {"conversation_stage": "information_collection"}
                )
                
                # Map field to extraction key
                field_to_key = {
                    "full name": "name",
                    "phone number": "phone",
                    "national id": "nid",
                    "address": "address",
                    "policy of interest": "policy",
                    "email": "email",
                }
                key = field_to_key.get(field_to_correct.lower())
                if key and extracted.get(key):
                    corrected_value = extracted.get(key)
            
            # Clear the field that needs correction
            if field_to_correct:
                field_map = {
                    "full name": "full_name",
                    "phone number": "phone_number",
                    "national id": "nid",
                    "address": "address",
                    "policy of interest": "policy_of_interest",
                    "email": "email",
                }
                field_key = field_map.get(field_to_correct.lower())
                
                if field_key and hasattr(state.collected_data, field_key):
                    if corrected_value:
                        # Update with corrected value
                        setattr(state.collected_data, field_key, corrected_value)
                        # Check if all fields are complete again
                        if state.collected_data.is_complete():
                            # Re-present summary for confirmation
                            summary = self._generate_information_summary(state)
                            state.awaiting_confirmation = True
                            state.confirmation_attempts = 1
                            await self.session_manager.save_session(state)
                            
                            reply = f"I've updated your {field_to_correct}. " + summary
                        else:
                            reply = f"I've updated your {field_to_correct}. Thank you! Let me continue collecting the remaining information."
                    else:
                        # Clear field and ask for correct value
                        setattr(state.collected_data, field_key, None)
                        reply = f"I'll help you correct that. Could you please provide your correct {field_to_correct}?"
                else:
                    reply = f"I'll help you correct that. Could you please provide your correct {field_to_correct}?"
            else:
                reply = "Could you please tell me which information needs to be corrected? For example, you can say 'the phone number is wrong' or 'change my address'."
            
            await self.session_manager.save_session(state)
            
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
        
        # Ambiguous response - ask for clarification
        state.confirmation_attempts += 1
        if state.confirmation_attempts >= 2:
            reply = "I want to make sure I understand. Please reply with 'Yes' if the information is correct, or tell me specifically what needs to be changed."
        else:
            reply = "Could you please confirm? Reply 'Yes' if the information is correct, or tell me what needs to be changed."
        
        await self.session_manager.save_session(state)
        
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

    async def _extract_correction_field(self, message: str, state: SessionState) -> Optional[str]:
        """Extract which field needs correction from message."""
        message_lower = message.lower()
        
        # Map keywords to field names
        field_keywords = {
            "name": ["name", "full name"],
            "phone": ["phone", "phone number", "mobile", "telephone"],
            "nid": ["national id", "nid", "id", "national identification"],
            "address": ["address", "location", "where i live"],
            "policy": ["policy", "insurance", "plan"],
            "email": ["email", "e-mail", "mail"],
        }
        
        for field, keywords in field_keywords.items():
            if any(keyword in message_lower for keyword in keywords) and any(kw in message_lower for kw in ["wrong", "incorrect", "change", "different", "update", "correct"]):
                # Map field name to display name
                field_display = {
                    "name": "full name",
                    "phone": "phone number",
                    "nid": "National ID",
                    "address": "address",
                    "policy": "policy of interest",
                    "email": "email",
                }
                return field_display.get(field, field)
        
        # Try LLM extraction if available (with retry)
        if self.llm_provider:
            try:
                prompt = f"""Extract which field needs to be corrected from this message: "{message}"
Available fields: full name, phone number, National ID, address, policy of interest, email.
Respond with just the field name if found, or "none" if unclear."""
                
                # Retry LLM call with exponential backoff (AC-022.3)
                async def _extract_field():
                    response = await self.llm_provider.generate_response(
                        [Message(role="user", content=prompt)],
                        config=LLMConfig(temperature=0.3, max_tokens=20)
                    )
                    return response.content.lower().strip()
                
                try:
                    extracted = await self.retry_service.retry_with_backoff(
                        _extract_field,
                        operation_name="LLM field extraction",
                        retryable_exceptions=[Exception],
                        non_retryable_exceptions=[]
                    )
                    if extracted != "none" and any(field in extracted for field in ["name", "phone", "nid", "address", "policy", "email"]):
                        return extracted
                except Exception as e:
                    logger.error(f"LLM field extraction failed after retries: {type(e).__name__}: {str(e)}")
                    # Fall through to return None
            except Exception as e:
                logger.error(f"LLM field extraction call error: {type(e).__name__}: {str(e)}")
        
        return None

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
            # Use LLM for intent classification (with retry)
            try:
                # Retry LLM call with exponential backoff (AC-022.3)
                async def _classify_intent():
                    return await self.llm_provider.classify_intent(message)
                
                try:
                    return await self.retry_service.retry_with_backoff(
                        _classify_intent,
                        operation_name="LLM intent classification",
                        retryable_exceptions=[Exception],
                        non_retryable_exceptions=[]
                    )
                except Exception as e:
                    logger.error(f"LLM intent classification failed after retries: {type(e).__name__}: {str(e)}")
                    # Fall through to keyword-based detection
            except Exception as e:
                logger.error(f"LLM intent classification call error: {type(e).__name__}: {str(e)}")
                # Fall through to keyword-based detection
        
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
    
    async def _get_recent_messages(self, conversation_id: int, limit: int = 5) -> List[Dict]:
        """Get recent messages for ambiguity detection."""
        messages = await self._get_messages(conversation_id, limit=limit)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') and msg.created_at else None
            }
            for msg in reversed(messages)  # Most recent first
        ]
    
    def _extract_recent_topics(self, recent_messages: List[Dict]) -> List[str]:
        """Extract topics from recent messages."""
        topics = []
        keywords = {
            "policy": ["policy", "coverage", "insurance", "plan"],
            "premium": ["premium", "cost", "price", "payment"],
            "term": ["term", "years", "duration", "period"],
            "medical": ["medical", "exam", "health", "medical exam"],
        }
        
        for msg in recent_messages:
            content = msg.get("content", "").lower()
            for topic, keys in keywords.items():
                if any(key in content for key in keys) and topic not in topics:
                    topics.append(topic)
        
        return topics[:3]  # Return top 3 topics
    
    def _can_resolve_ambiguity_with_context(
        self,
        ambiguity_result,
        context: Dict[str, Any],
        recent_messages: List[Dict]
    ) -> bool:
        """
        Check if ambiguity can be resolved using context.
        
        Returns True if context provides enough information to resolve ambiguity.
        """
        if not ambiguity_result.is_ambiguous:
            return True
        
        # If it's a pronoun ambiguity and we have recent context, try to resolve
        if ambiguity_result.ambiguity_type == "pronoun":
            # Check if recent messages mention specific items (policies, etc.)
            recent_text = " ".join([msg.get("content", "") for msg in recent_messages[-3:] if msg.get("role") == "assistant"]).lower()
            
            # If recent messages mention specific policies/items, we might be able to infer
            if context.get("policies_discussed"):
                # If only one policy discussed, can infer
                if len(context.get("policies_discussed", [])) == 1:
                    return True
            
            # Check for specific mentions
            if any(word in recent_text for word in ["term life", "whole life", "policy", "coverage"]):
                # Might be able to infer from context
                return len(context.get("policies_discussed", [])) <= 2
        
        # If it's vague language but recent context is clear
        if ambiguity_result.ambiguity_type == "vague":
            # If we just discussed something specific, can infer
            if recent_messages and recent_messages[-1].get("role") == "assistant":
                recent_content = recent_messages[-1].get("content", "").lower()
                if any(word in recent_content for word in ["policy", "coverage", "premium", "term"]):
                    return True
        
        # If it's contradictory, need clarification
        if ambiguity_result.ambiguity_type == "contradictory":
            return False
        
        # If multiple interpretations, need clarification
        if ambiguity_result.ambiguity_type == "multiple_interpretations":
            # Only can resolve if one interpretation is much more likely given context
            return False
        
        # Default: cannot resolve with context
        return False
