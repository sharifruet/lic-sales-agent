"""LLM Provider abstraction and base classes."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Intent(Enum):
    """Customer intent types."""
    GREETING = "greeting"
    QUESTION = "question"
    OBJECTION = "objection"
    INTEREST = "interest"
    EXIT = "exit"
    INFORMATION_REQUEST = "information_request"
    POLICY_COMPARISON = "policy_comparison"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Conversation message."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[str] = None


@dataclass
class LLMConfig:
    """LLM configuration."""
    temperature: float = 0.7
    max_tokens: int = 500
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


@dataclass
class LLMResponse:
    """LLM response."""
    content: str
    model: str
    tokens_used: int = 0
    finish_reason: str = "stop"


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Message],
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate response from LLM."""
        pass
    
    @abstractmethod
    async def classify_intent(self, message: str) -> Intent:
        """Classify user intent."""
        pass
    
    @abstractmethod
    async def extract_entities(
        self,
        message: str,
        entity_types: List[str]
    ) -> Dict[str, Any]:
        """Extract structured entities from message."""
        pass

