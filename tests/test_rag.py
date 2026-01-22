"""Tests for RAG ingestion and retriever skeleton."""

from datetime import datetime, timezone

import pytest

from chains.parsers import parse_retriever_output
from chains.runnables import build_retriever_chain
from graph.nodes import retriever as retriever_node
from rag import ingest, retriever
from rag.schemas import DocumentMetadata
from state.schemas import ConversationState, Message, MessageType


SAMPLE_DOCS = [
    (
        "Whole life policies provide lifetime coverage with fixed premiums.",
        DocumentMetadata(source="kb/whole_life.md", category="whole-life"),
    ),
    (
        "Term life policies are affordable and cover a set period (10-30 years).",
        DocumentMetadata(source="kb/term_life.md", category="term-life"),
    ),
]


def test_ingest_and_retrieve_roundtrip() -> None:
    ingest.ingest_documents(SAMPLE_DOCS)
    retriever_instance = retriever.get_retriever()
    results = retriever_instance("Tell me about term life", top_k=1)
    assert results, "Expected at least one retrieval result"
    assert results[0]["source"] == "kb/term_life.md"


def test_get_retriever_without_documents_errors() -> None:
    ingest.ingest_documents([])
    with pytest.raises(ValueError):
        retriever.get_retriever()


def test_retrieve_context_updates_state() -> None:
    ingest.ingest_documents(SAMPLE_DOCS)
    state = ConversationState(
        messages=[
            Message(
                role="user",
                content="What is the difference between whole and term life?",
                timestamp=datetime.now(timezone.utc),
                message_type=MessageType.USER,
            )
        ],
        current_objective="Explain policy differences",
    )
    updated_state = retriever_node.retrieve_context(state)
    assert updated_state.retrieved_context, "retrieved_context should be populated"
    assert updated_state.messages[-1].message_type is MessageType.RETRIEVER


def test_parse_retriever_output_handles_json() -> None:
    payload = {
        "results": [
            {
                "content": "Sample content",
                "source": "kb/sample.md",
                "score": 0.5,
            }
        ]
    }
    parsed = parse_retriever_output(payload)
    assert parsed.results[0].content == "Sample content"
