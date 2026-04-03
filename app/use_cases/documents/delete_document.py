from uuid import UUID

from app.domain.errors import DocumentNotFoundError
from app.providers import DocumentRepository


class DeleteDocumentUseCase:
    """Use case для удаления документа."""

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._document_repo = document_repo

    async def execute(self, document_id: UUID) -> None:
        document = await self._document_repo.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        
        await self._document_repo.delete(document_id)
