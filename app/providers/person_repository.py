from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Person


class PersonRepository(ABC):
    """Репозиторий для работы с карточками репрессированных."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Person | None:
        """Получить карточку по ID."""
        ...

    @abstractmethod
    async def find_duplicate(self, full_name: str, birth_year: int) -> Person | None:
        """Найти дубликат по имени и году рождения."""
        ...

    @abstractmethod
    async def list(
        self,
        name: str | None,
        region: str | None,
        accusation: str | None,
        limit: int,
        offset: int,
    ) -> list[Person]:
        """Получить список карточек с фильтрацией."""
        ...

    @abstractmethod
    async def save(self, person: Person) -> Person:
        """Сохранить (создать или обновить) карточку."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить карточку."""
        ...
