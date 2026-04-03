from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Document


class DocumentRepository(ABC):
    """Репозиторий для работы с документами."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Document | None:
        """Получить документ по ID."""
        ...

    @abstractmethod
    async def get_by_person_id(self, person_id: UUID) -> list[Document]:
        """Получить все документы для карточки."""
        ...

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Сохранить документ."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить документ."""
        ...
