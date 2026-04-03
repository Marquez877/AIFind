from uuid import UUID

from app.domain.errors import PersonNotFoundError
from app.providers import PersonRepository


class DeletePersonUseCase:
    """Use case для удаления карточки репрессированного."""

    def __init__(self, repo: PersonRepository) -> None:
        self._repo = repo

    async def execute(self, person_id: UUID) -> None:
        existing = await self._repo.get_by_id(person_id)
        if existing is None:
            raise PersonNotFoundError(person_id)
        
        await self._repo.delete(person_id)
