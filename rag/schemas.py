"""Document and chunk metadata schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Placeholder metadata schema."""

    source: str
    category: str | None = None


class ChunkMetadata(BaseModel):
    """Placeholder chunk schema."""

    document_id: str
    position: int

