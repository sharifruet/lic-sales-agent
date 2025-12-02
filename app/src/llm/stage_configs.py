"""Stage-specific LLM configurations following LLM Integration Design."""
from app.src.llm.providers.llm_provider import LLMConfig
from app.src.services.session_manager import ConversationStage


# Stage-specific LLM configurations from LLM Integration Design Document
STAGE_CONFIGS = {
    ConversationStage.INTRODUCTION: LLMConfig(
        temperature=0.8,  # More friendly, varied greetings
        max_tokens=150
    ),
    ConversationStage.QUALIFICATION: LLMConfig(
        temperature=0.6,  # More consistent questions
        max_tokens=200
    ),
    ConversationStage.INFORMATION: LLMConfig(
        temperature=0.7,  # Balanced explanation
        max_tokens=600    # Longer for policy details
    ),
    ConversationStage.PERSUASION: LLMConfig(
        temperature=0.7,  # Natural persuasion
        max_tokens=400
    ),
    ConversationStage.INFORMATION_COLLECTION: LLMConfig(
        temperature=0.5,  # More structured, less creative
        max_tokens=200
    ),
    ConversationStage.OBJECTION_HANDLING: LLMConfig(
        temperature=0.7,  # Empathetic but clear
        max_tokens=300
    ),
    ConversationStage.CLOSING: LLMConfig(
        temperature=0.6,  # Clear and direct
        max_tokens=150
    ),
}

# Default config
DEFAULT_CONFIG = LLMConfig(
    temperature=0.7,
    max_tokens=500
)


def get_stage_config(stage: ConversationStage) -> LLMConfig:
    """Get LLM configuration for specific conversation stage."""
    return STAGE_CONFIGS.get(stage, DEFAULT_CONFIG)

