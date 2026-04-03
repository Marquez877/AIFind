from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Person
from app.infrastructure.db.models import PersonModel
from app.providers import PersonRepository


class SQLAlchemyPersonRepository(PersonRepository):
    """SQLAlchemy реализация репозитория для карточек репрессированных."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: PersonModel) -> Person:
        return Person(
            id=model.id,
            full_name=model.full_name,
            birth_year=model.birth_year,
            death_year=model.death_year,
            region=model.region,
            accusation=model.accusation,
            biography=model.biography,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: Person) -> PersonModel:
        return PersonModel(
            id=entity.id,
            full_name=entity.full_name,
            birth_year=entity.birth_year,
            death_year=entity.death_year,
            region=entity.region,
            accusation=entity.accusation,
            biography=entity.biography,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Person | None:
        result = await self._session.execute(
            select(PersonModel).where(PersonModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def find_duplicate(self, full_name: str, birth_year: int) -> Person | None:
        """Поиск дубликата по имени (case-insensitive) и году рождения."""
        result = await self._session.execute(
            select(PersonModel).where(
                func.lower(PersonModel.full_name) == full_name.lower(),
                PersonModel.birth_year == birth_year,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list(
        self,
        name: str | None,
        region: str | None,
        accusation: str | None,
        limit: int,
        offset: int,
    ) -> list[Person]:
        query = select(PersonModel)

        if name is not None:
            query = query.where(PersonModel.full_name.ilike(f"%{name}%"))
        if region is not None:
            query = query.where(PersonModel.region.ilike(f"%{region}%"))
        if accusation is not None:
            query = query.where(PersonModel.accusation.ilike(f"%{accusation}%"))

        query = query.order_by(PersonModel.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def save(self, person: Person) -> Person:
        existing_result = await self._session.execute(
            select(PersonModel).where(PersonModel.id == person.id)
        )
        model = existing_result.scalar_one_or_none()

        if model is None:
            model = self._to_model(person)
            self._session.add(model)
        else:
            model.full_name = person.full_name
            model.birth_year = person.birth_year
            model.death_year = person.death_year
            model.region = person.region
            model.accusation = person.accusation
            model.biography = person.biography
            model.updated_at = person.updated_at

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        result = await self._session.execute(
            select(PersonModel).where(PersonModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return

        await self._session.delete(model)
        await self._session.commit()
