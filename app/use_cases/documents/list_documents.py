from uuid import UUID

from app.domain.entities import Document
from app.domain.errors import PersonNotFoundError
from app.providers import DocumentRepository, PersonRepository


class ListDocumentsUseCase:
    """Use case для получения списка документов карточки."""

    def __init__(self, person_repo: PersonRepository, document_repo: DocumentRepository) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo

    async def execute(self, person_id: UUID) -> list[Document]:
        # Проверить что карточка существует
        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        return await self._document_repo.get_by_person_id(person_id)
