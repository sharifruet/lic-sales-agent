"""Data ingestion utilities for vector stores."""

from __future__ import annotations

from typing import Iterable, List, Tuple, Union

from rag.schemas import DocumentMetadata

_DOCUMENT_STORE: List[Tuple[str, DocumentMetadata]] = []


def _coerce_metadata(metadata: Union[DocumentMetadata, dict]) -> DocumentMetadata:
    if isinstance(metadata, DocumentMetadata):
        return metadata
    if isinstance(metadata, dict):
        return DocumentMetadata(**metadata)
    raise TypeError("Document metadata must be a DocumentMetadata instance or dict.")


def ingest_documents(documents: Iterable[Tuple[str, Union[DocumentMetadata, dict]]]) -> None:
    """Simple in-memory ingestion for development and testing."""
    _DOCUMENT_STORE.clear()
    for content, metadata in documents:
        _DOCUMENT_STORE.append((content, _coerce_metadata(metadata)))


def get_document_store() -> List[Tuple[str, DocumentMetadata]]:
    """Return the in-memory document store."""
    return list(_DOCUMENT_STORE)

