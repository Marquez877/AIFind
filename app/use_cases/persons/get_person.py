from uuid import UUID

from app.domain.entities import Person
from app.domain.errors import PersonNotFoundError
from app.providers import PersonRepository


class GetPersonUseCase:
    """Use case для получения карточки репрессированного."""

    def __init__(self, repo: PersonRepository) -> None:
        self._repo = repo

    async def execute(self, person_id: UUID) -> Person:
        person = await self._repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)
        return person
