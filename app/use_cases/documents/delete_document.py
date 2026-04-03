from uuid import UUID

from app.domain.services.document_storage import DocumentStorage
from app.domain.errors import DocumentNotFoundError
from app.providers import DocumentRepository


class DeleteDocumentUseCase:
    """Use case для удаления документа."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        document_storage: DocumentStorage | None = None,
    ) -> None:
        self._document_repo = document_repo
        self._document_storage = document_storage

    async def execute(self, document_id: UUID) -> None:
        document = await self._document_repo.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        if document.original_file_path and self._document_storage is not None:
            await self._document_storage.delete_original(document.original_file_path)

        await self._document_repo.delete(document_id)
