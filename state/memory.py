"""Conversation memory policies."""

from __future__ import annotations

from datetime import datetime, timezone

from state.schemas import ConversationState, MessageType


def apply_short_term_memory(state: ConversationState, max_messages: int = 20) -> ConversationState:
    """Trim conversation history to the most recent messages."""
    if len(state.messages) > max_messages:
        state.messages = state.messages[-max_messages:]
    for message in state.messages:
        if message.timestamp is None:
            message.timestamp = datetime.now(timezone.utc)
    return state


def apply_long_term_memory(state: ConversationState, max_notes: int = 50) -> ConversationState:
    """Persist high-level notes from assistant messages."""
    if state.messages:
        latest = state.messages[-1]
        if latest.message_type in {MessageType.ASSISTANT, MessageType.SYSTEM}:
            note = latest.content.strip()
            if note:
                state.long_term_notes.append(note)
                if len(state.long_term_notes) > max_notes:
                    state.long_term_notes = state.long_term_notes[-max_notes:]
    return state

