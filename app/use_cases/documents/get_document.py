from uuid import UUID

from app.domain.entities import Document
from app.domain.errors import DocumentNotFoundError
from app.providers import DocumentRepository


class GetDocumentUseCase:
    """Use case для получения документа по ID."""

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._document_repo = document_repo

    async def execute(self, document_id: UUID) -> Document:
        document = await self._document_repo.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return document
