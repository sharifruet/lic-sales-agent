"""FastAPI router bridging HTTP requests to the LangGraph conversation engine."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from graph.build_graph import build_conversation_graph
from state.schemas import ConversationState, Message, MessageType

api_router = APIRouter(prefix="/api", tags=["conversation"])


class ConversationStore:
    """In-memory store for demo purposes."""

    def __init__(self) -> None:
        self._store: dict[str, ConversationState] = {}

    def get(self, conversation_id: str) -> ConversationState:
        if conversation_id not in self._store:
            self._store[conversation_id] = ConversationState()
        return self._store[conversation_id]

    def set(self, conversation_id: str, state: ConversationState) -> None:
        self._store[conversation_id] = state


conversation_store = ConversationStore()
conversation_graph = build_conversation_graph()


@api_router.post("/conversations/{conversation_id}/messages")
async def post_message(conversation_id: str, payload: dict) -> dict:
    """Accept a user message and return the updated conversation state."""
    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=422, detail="content is required")

    state = conversation_store.get(conversation_id)
    state.messages.append(
        Message(
            role="user",
            content=content,
            message_type=MessageType.USER,
            timestamp=datetime.now(timezone.utc),
        )
    )

    state.current_objective = payload.get("objective") or state.current_objective
    state.metadata.update(payload.get("metadata") or {})

    updated_state = conversation_graph.run_turn(state)
    conversation_store.set(conversation_id, updated_state)

    return {
        "conversation_id": conversation_id,
        "messages": [message.model_dump() for message in updated_state.messages],
        "plan_steps": updated_state.plan_steps,
        "retrieved_context": [doc.model_dump() for doc in updated_state.retrieved_context],
        "metadata": updated_state.metadata,
    }


@api_router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict:
    state = conversation_store.get(conversation_id)
    return {
        "conversation_id": conversation_id,
        "messages": [message.model_dump() for message in state.messages],
        "plan_steps": state.plan_steps,
        "long_term_notes": state.long_term_notes,
        "metadata": state.metadata,
    }

