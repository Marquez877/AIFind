from datetime import datetime
from uuid import UUID

from app.domain.entities import Person
from app.domain.errors import PersonAlreadyExistsError, PersonNotFoundError
from app.providers import PersonRepository


class UpdatePersonUseCase:
    """Use case для обновления карточки репрессированного."""

    def __init__(self, repo: PersonRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        person_id: UUID,
        full_name: str | None = None,
        birth_year: int | None = None,
        death_year: int | None = None,
        region: str | None = None,
        accusation: str | None = None,
        biography: str | None = None,
    ) -> Person:
        existing = await self._repo.get_by_id(person_id)
        if existing is None:
            raise PersonNotFoundError(person_id)

        new_name = full_name if full_name is not None else existing.full_name
        new_birth_year = birth_year if birth_year is not None else existing.birth_year

        # Проверка на дубликат если меняется имя или год рождения
        if full_name is not None or birth_year is not None:
            duplicate = await self._repo.find_duplicate(new_name, new_birth_year)
            if duplicate is not None and duplicate.id != person_id:
                raise PersonAlreadyExistsError(new_name, new_birth_year, duplicate.id)

        updated_person = Person(
            id=existing.id,
            full_name=new_name,
            birth_year=new_birth_year,
            death_year=death_year if death_year is not None else existing.death_year,
            region=region if region is not None else existing.region,
            accusation=accusation if accusation is not None else existing.accusation,
            biography=biography if biography is not None else existing.biography,
            created_at=existing.created_at,
            updated_at=datetime.utcnow(),
        )
        return await self._repo.save(updated_person)
