"""Conversation state schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Categories for conversation messages."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    PLANNER = "planner"
    RETRIEVER = "retriever"
    TOOL = "tool"


class Message(BaseModel):
    """Single conversation message."""

    role: str
    content: str
    timestamp: datetime | None = None
    message_type: MessageType = MessageType.USER
    metadata: Dict[str, str] = Field(default_factory=dict)


class PlanDecision(str, Enum):
    """Possible planner decisions."""

    CONTINUE = "continue"
    RETRIEVE = "retrieve"
    TOOL = "tool"
    END = "end"


class RetrievedDocument(BaseModel):
    """Document snippet retrieved for the current turn."""

    content: str
    source: Optional[str] = None
    score: Optional[float] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class ConversationState(BaseModel):
    """Conversation state shared across LangGraph nodes."""

    messages: List[Message] = Field(default_factory=list)
    lead_id: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    current_objective: Optional[str] = None
    plan_steps: List[str] = Field(default_factory=list)
    planner_rationale: Optional[str] = None
    pending_tool_call: Optional[str] = None
    next_action: Optional[PlanDecision] = None
    retrieved_context: List[RetrievedDocument] = Field(default_factory=list)
    long_term_notes: List[str] = Field(default_factory=list)

