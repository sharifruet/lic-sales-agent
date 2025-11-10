"""Retriever node for fetching supporting knowledge."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from chains.parsers import RetrieverOutput, parse_retriever_output
from chains.runnables import RetrieverChain, build_retriever_chain
from state.schemas import ConversationState, Message, MessageType, RetrievedDocument


def _last_user_message(state: ConversationState) -> Optional[str]:
    for message in reversed(state.messages):
        if message.message_type is MessageType.USER:
            return message.content
    return None


def _build_retriever_inputs(state: ConversationState) -> Dict[str, Any]:
    query = _last_user_message(state) or state.current_objective or ""
    return {
        "query": query,
        "plan_steps": state.plan_steps,
        "metadata": state.metadata,
        "top_k": 3,
    }


def _append_retriever_message(state: ConversationState, documents: RetrieverOutput) -> None:
    summary = ", ".join(
        filter(None, [doc.source for doc in documents.results])
    ) or "No sources"
    state.messages.append(
        Message(
            role="system",
            content=f"Retrieved {len(documents.results)} documents: {summary}",
            timestamp=datetime.now(timezone.utc),
            message_type=MessageType.RETRIEVER,
        )
    )


def retrieve_context(
    state: ConversationState,
    chain: Optional[RetrieverChain] = None,
) -> ConversationState:
    """Run the retriever chain and update conversation state."""
    retriever_chain = chain or build_retriever_chain()
    raw_output = retriever_chain(_build_retriever_inputs(state))
    retriever_output = parse_retriever_output(raw_output)

    state.retrieved_context = retriever_output.results
    _append_retriever_message(state, retriever_output)
    return state

