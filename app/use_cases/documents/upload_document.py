from uuid import uuid4

from app.config import settings
from app.domain.entities import Document
from app.domain.entities.chunk import Chunk
from app.domain.errors import PersonNotFoundError
from app.domain.services.document_storage import DocumentStorage
from app.domain.value_objects.document_type import DocumentType
from app.infrastructure.ai.embedding_service import EmbeddingService, chunk_text
from app.infrastructure.parsers import ParserFactory
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.providers import DocumentRepository, PersonRepository


# Deprecated: используем DocumentType.supported_extensions()
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}


class UploadDocumentUseCase:
    """Use case для загрузки документа к карточке с автоматическим chunking."""

    def __init__(
        self,
        person_repo: PersonRepository,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository | None = None,
        embedding_service: EmbeddingService | None = None,
        parser_factory: ParserFactory | None = None,
        document_storage: DocumentStorage | None = None,
    ) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo
        self._chunk_repo = chunk_repo
        self._embedding_service = embedding_service
        self._parser_factory = parser_factory or ParserFactory()
        self._document_storage = document_storage

    async def execute(
        self,
        person_id: str,
        filename: str,
        content: str | bytes,
        generate_embeddings: bool = True,
    ) -> Document:
        """
        Загрузить документ к карточке.

        Args:
            person_id: ID карточки
            filename: Имя файла
            content: Содержимое (str для текстовых, bytes для бинарных)
            generate_embeddings: Генерировать ли эмбеддинги

        Returns:
            Сохранённый документ
        """
        from uuid import UUID
        
        person_uuid = UUID(person_id)
        
        # Проверить что карточка существует
        person = await self._person_repo.get_by_id(person_uuid)
        if person is None:
            raise PersonNotFoundError(person_uuid)

        # Парсинг содержимого файла
        original_file_path: str | None = None
        if isinstance(content, bytes):
            text_content = await self._parser_factory.parse_file(content, filename)
            doc_type = DocumentType.from_filename(filename)
            if doc_type == DocumentType.PDF and self._document_storage is not None:
                original_file_path = await self._document_storage.save_original(filename, content)
        else:
            text_content = content

        document = Document(
            id=uuid4(),
            person_id=person_uuid,
            filename=filename,
            content=text_content,
            original_file_path=original_file_path,
        )
        saved_doc = await self._document_repo.save(document)

        # Create chunks with embeddings if services are available
        if self._chunk_repo is not None:
            await self._create_chunks(saved_doc, generate_embeddings)

        return saved_doc

    async def execute_from_bytes(
        self,
        person_id: str,
        filename: str,
        file_bytes: bytes,
        generate_embeddings: bool = True,
    ) -> Document:
        """
        Загрузить документ из бинарных данных (для multipart/form-data).

        Args:
            person_id: ID карточки
            filename: Имя файла
            file_bytes: Бинарное содержимое файла
            generate_embeddings: Генерировать ли эмбеддинги

        Returns:
            Сохранённый документ
        """
        return await self.execute(
            person_id=person_id,
            filename=filename,
            content=file_bytes,
            generate_embeddings=generate_embeddings,
        )

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
