"""Repository for document chunks with vector similarity search."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chunk import Chunk
from app.infrastructure.db.models import ChunkModel


@dataclass
class ChunkSearchResult:
    """Result of a semantic search including similarity score."""
    chunk: Chunk
    similarity: float


class ChunkRepository:
    """Repository for storing and searching document chunks."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: ChunkModel) -> Chunk:
        return Chunk(
            id=model.id,
            document_id=model.document_id,
            content=model.content,
            chunk_index=model.chunk_index,
            embedding=list(model.embedding) if model.embedding is not None else None,
            created_at=model.created_at,
        )

    async def save(self, chunk: Chunk) -> Chunk:
        """Save a chunk to the database."""
        model = ChunkModel(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            embedding=chunk.embedding,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def save_batch(self, chunks: list[Chunk]) -> list[Chunk]:
        """Save multiple chunks in a single transaction."""
        models = [
            ChunkModel(
                id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                embedding=chunk.embedding,
            )
            for chunk in chunks
        ]
        self._session.add_all(models)
        await self._session.commit()
        
        for model in models:
            await self._session.refresh(model)
        
        return [self._to_entity(model) for model in models]

    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        """Get all chunks for a document."""
        result = await self._session.execute(
            select(ChunkModel)
            .where(ChunkModel.document_id == document_id)
            .order_by(ChunkModel.chunk_index)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def delete_by_document_id(self, document_id: UUID) -> int:
        """Delete all chunks for a document. Returns number of deleted chunks."""
        result = await self._session.execute(
            select(ChunkModel).where(ChunkModel.document_id == document_id)
        )
        models = result.scalars().all()
        count = len(models)
        
        for model in models:
            await self._session.delete(model)
        
        await self._session.commit()
        return count

    async def search_similar(
        self,
        query_embedding: list[float],
        document_ids: list[UUID],
        limit: int = 3,
    ) -> list[ChunkSearchResult]:
        """Find most similar chunks using cosine similarity.
        
        Args:
            query_embedding: The embedding vector to search for
            document_ids: List of document IDs to search within
            limit: Maximum number of results to return
        
        Returns:
            List of ChunkSearchResult ordered by similarity (highest first)
        """
        if not document_ids:
            return []
        
        # Convert embedding to PostgreSQL array format
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        # Use pgvector's cosine distance operator (<=>)
        # Cosine similarity = 1 - cosine distance
        query = text("""
            SELECT 
                id,
                document_id,
                content,
                chunk_index,
                embedding,
                created_at,
                1 - (embedding <=> :embedding::vector) as similarity
            FROM chunks
            WHERE document_id = ANY(:document_ids)
              AND embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)
        
        result = await self._session.execute(
            query,
            {
                "embedding": embedding_str,
                "document_ids": document_ids,
                "limit": limit,
            }
        )
        
        rows = result.fetchall()
        
        return [
            ChunkSearchResult(
                chunk=Chunk(
                    id=row.id,
                    document_id=row.document_id,
                    content=row.content,
                    chunk_index=row.chunk_index,
                    embedding=list(row.embedding) if row.embedding else None,
                    created_at=row.created_at,
                ),
                similarity=float(row.similarity),
            )
            for row in rows
        ]

    async def search_by_person(
        self,
        query_embedding: list[float],
        person_id: UUID,
        limit: int = 3,
    ) -> list[ChunkSearchResult]:
        """Find most similar chunks for a person's documents.
        
        This is a convenience method that searches across all documents
        belonging to a specific person.
        """
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        query = text("""
            SELECT 
                c.id,
                c.document_id,
                c.content,
                c.chunk_index,
                c.embedding,
                c.created_at,
                1 - (c.embedding <=> :embedding::vector) as similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.person_id = :person_id
              AND c.embedding IS NOT NULL
            ORDER BY c.embedding <=> :embedding::vector
            LIMIT :limit
        """)
        
        result = await self._session.execute(
            query,
            {
                "embedding": embedding_str,
                "person_id": person_id,
                "limit": limit,
            }
        )
        
        rows = result.fetchall()
        
        return [
            ChunkSearchResult(
                chunk=Chunk(
                    id=row.id,
                    document_id=row.document_id,
                    content=row.content,
                    chunk_index=row.chunk_index,
                    embedding=list(row.embedding) if row.embedding else None,
                    created_at=row.created_at,
                ),
                similarity=float(row.similarity),
            )
            for row in rows
        ]
