from uuid import uuid4

from app.domain.entities import Person
from app.domain.errors import PersonAlreadyExistsError
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.providers import PersonRepository


class CreatePersonUseCase:
    """Use case для создания карточки репрессированного."""

    def __init__(
        self,
        repo: PersonRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self._repo = repo
        self._embedding_service = embedding_service

    async def execute(
        self,
        full_name: str,
        birth_year: int,
        death_year: int | None,
        region: str,
        accusation: str,
        biography: str,
    ) -> Person:
        # Проверка на дубликат (имя + год рождения)
        existing = await self._repo.find_duplicate(full_name, birth_year)
        if existing is not None:
            raise PersonAlreadyExistsError(full_name, birth_year, existing.id)

        person = Person(
            id=uuid4(),
            full_name=full_name,
            birth_year=birth_year,
            death_year=death_year,
            region=region,
            accusation=accusation,
            biography=biography,
        )
        saved = await self._repo.save(person)
        embedding = await self._embedding_service.get_embedding(saved.biography)
        await self._repo.set_biography_embedding(saved.id, embedding)
        return saved
