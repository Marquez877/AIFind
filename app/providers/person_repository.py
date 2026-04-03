from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Person


@dataclass
class DuplicateMatch:
    """Кандидат на дубликат с оценками похожести."""

    person: Person
    score: float
    name_similarity: float
    biography_similarity: float


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
    async def search(
        self,
        name: str | None = None,
        region: str | None = None,
        accusation_type: str | None = None,
        birth_year_from: int | None = None,
        birth_year_to: int | None = None,
        death_year_from: int | None = None,
        death_year_to: int | None = None,
        verification_status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        """Расширенный поиск с фильтрами и пагинацией."""
        ...

    @abstractmethod
    async def get_filter_values(self):
        """Получить доступные значения для фильтров."""
        ...

    @abstractmethod
    async def save(self, person: Person) -> Person:
        """Сохранить (создать или обновить) карточку."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить карточку."""
        ...

    @abstractmethod
    async def get_pending_moderation(self, limit: int = 50, offset: int = 0) -> list[Person]:
        """Получить записи, ожидающие модерации."""
        ...

    @abstractmethod
    async def find_potential_duplicates(
        self,
        full_name: str,
        birth_year: int,
        biography_embedding: list[float] | None,
        limit: int = 5,
    ) -> list[DuplicateMatch]:
        """Найти потенциальные дубли по нечёткому совпадению и эмбеддингам."""
        ...

    @abstractmethod
    async def set_biography_embedding(self, person_id: UUID, embedding: list[float]) -> None:
        """Сохранить эмбеддинг биографии для карточки."""
        ...
