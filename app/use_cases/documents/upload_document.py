from uuid import uuid4

from app.domain.entities import Document
from app.domain.errors import PersonNotFoundError
from app.providers import DocumentRepository, PersonRepository


ALLOWED_EXTENSIONS = {".txt", ".md"}


class UploadDocumentUseCase:
    """Use case для загрузки документа к карточке."""

    def __init__(self, person_repo: PersonRepository, document_repo: DocumentRepository) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo

    async def execute(
        self,
        person_id: str,
        filename: str,
        content: str,
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
        return await self._document_repo.save(document)
