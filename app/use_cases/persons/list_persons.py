from app.domain.entities import Person
from app.providers import PersonRepository


class ListPersonsUseCase:
    """Use case для получения списка карточек с фильтрацией."""

    def __init__(self, repo: PersonRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        name: str | None = None,
        region: str | None = None,
        accusation: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Person]:
        return await self._repo.list(name, region, accusation, limit, offset)
