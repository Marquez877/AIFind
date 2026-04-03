"""Chunk entity for document fragments with embeddings."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Chunk:
    """Represents a chunk of a document with optional embedding vector."""

    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    embedding: list[float] | None
    created_at: datetime

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has an embedding vector."""
        return self.embedding is not None and len(self.embedding) > 0
