"""Retriever interfaces for LangGraph nodes."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, Dict, List

from rag.ingest import get_document_store
from rag.schemas import DocumentMetadata


class SimpleRetriever:
    """Lightweight retriever used during early migration."""

    def __init__(self, documents: List[tuple[str, DocumentMetadata]]) -> None:
        self._documents = documents

    def _score(self, query: str, content: str) -> float:
        return SequenceMatcher(None, query.lower(), content.lower()).ratio()

    def invoke(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        scored = []
        for content, metadata in self._documents:
            score = self._score(query, content)
            scored.append((score, content, metadata))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for score, content, metadata in scored[:top_k]:
            results.append(
                {
                    "content": content,
                    "source": metadata.source,
                    "score": score,
                    "metadata": metadata.model_dump(),
                }
            )
        return results

    def __call__(self, query: str, *, top_k: int = 3) -> List[Dict[str, Any]]:
        return self.invoke(query=query, top_k=top_k)


def get_retriever() -> SimpleRetriever:
    """Return the configured retriever (vector/hybrid)."""
    documents = get_document_store()
    if not documents:
        raise ValueError("Document store is empty. Call ingest_documents() first.")
    return SimpleRetriever(documents)

