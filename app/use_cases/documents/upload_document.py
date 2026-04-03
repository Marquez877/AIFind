from uuid import uuid4

from app.config import settings
from app.domain.entities import Document
from app.domain.entities.chunk import Chunk
from app.domain.errors import PersonNotFoundError
from app.infrastructure.ai.embedding_service import EmbeddingService, chunk_text
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.providers import DocumentRepository, PersonRepository


ALLOWED_EXTENSIONS = {".txt", ".md"}


class UploadDocumentUseCase:
    """Use case для загрузки документа к карточке с автоматическим chunking."""

    def __init__(
        self,
        person_repo: PersonRepository,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo
        self._chunk_repo = chunk_repo
        self._embedding_service = embedding_service

    async def execute(
        self,
        person_id: str,
        filename: str,
        content: str,
        generate_embeddings: bool = True,
    ) -> Document:
        from uuid import UUID
        
        person_uuid = UUID(person_id)
        
        # Проверить что карточка существует
        person = await self._person_repo.get_by_id(person_uuid)
        if person is None:
            raise PersonNotFoundError(person_uuid)

        document = Document(
            id=uuid4(),
            person_id=person_uuid,
            filename=filename,
            content=content,
        )
        saved_doc = await self._document_repo.save(document)

        # Create chunks with embeddings if services are available
        if self._chunk_repo is not None:
            await self._create_chunks(saved_doc, generate_embeddings)

        return saved_doc

    async def _create_chunks(self, document: Document, generate_embeddings: bool) -> None:
        """Split document into chunks and optionally generate embeddings."""
        # Split content into chunks
        chunk_texts = chunk_text(
            document.content,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )

        if not chunk_texts:
            return

        # Generate embeddings if requested and service is available
        embeddings: list[list[float] | None] = [None] * len(chunk_texts)
        
        if generate_embeddings and self._embedding_service is not None:
            try:
                embeddings = await self._embedding_service.get_embeddings_batch(chunk_texts)
            except Exception:
                # If embedding generation fails, continue without embeddings
                pass

        # Create chunk entities
        chunks = [
            Chunk(
                id=uuid4(),
                document_id=document.id,
                content=text,
                chunk_index=idx,
                embedding=embeddings[idx],
                created_at=document.uploaded_at,
            )
            for idx, text in enumerate(chunk_texts)
        ]

        # Save all chunks
        await self._chunk_repo.save_batch(chunks)
