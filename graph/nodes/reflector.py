"""Reflection node for summarising or adjusting strategy."""

from __future__ import annotations

from datetime import datetime, timezone

from state.schemas import ConversationState, Message, MessageType


def reflect_on_conversation(state: ConversationState) -> ConversationState:
    """Append a brief reflection message if plan steps exist."""
    if not state.plan_steps:
        return state

    summary = "; ".join(state.plan_steps[:2])
    state.messages.append(
        Message(
            role="system",
            content=f"Reflection: next steps -> {summary}",
            timestamp=datetime.now(timezone.utc),
            message_type=MessageType.SYSTEM,
        )
    )
    return state

