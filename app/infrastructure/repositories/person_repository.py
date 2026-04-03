from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Person
from app.infrastructure.db.models import PersonModel
from app.providers import PersonRepository


@dataclass
class SearchResult:
    """Result of paginated search."""
    items: list[Person]
    total: int


@dataclass
class FilterValues:
    """Available filter values."""
    regions: list[str]
    accusation_types: list[str]
    min_birth_year: int | None
    max_birth_year: int | None
    min_death_year: int | None
    max_death_year: int | None


class SQLAlchemyPersonRepository(PersonRepository):
    """SQLAlchemy реализация репозитория для карточек репрессированных."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: PersonModel) -> Person:
        from app.domain.value_objects import VerificationStatus
        
        return Person(
            id=model.id,
            full_name=model.full_name,
            birth_year=model.birth_year,
            death_year=model.death_year,
            region=model.region,
            accusation=model.accusation,
            biography=model.biography,
            verification_status=VerificationStatus(model.verification_status),
            verified_at=model.verified_at,
            verified_by=model.verified_by,
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
            verification_status=entity.verification_status.value,
            verified_at=entity.verified_at,
            verified_by=entity.verified_by,
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
    ) -> SearchResult:
        """Расширенный поиск с фильтрами и пагинацией."""
        query = select(PersonModel)
        count_query = select(func.count(PersonModel.id))

        # Apply filters
        filters = []
        if name:
            filters.append(PersonModel.full_name.ilike(f"%{name}%"))
        if region:
            filters.append(PersonModel.region.ilike(f"%{region}%"))
        if accusation_type:
            filters.append(PersonModel.accusation.ilike(f"%{accusation_type}%"))
        if birth_year_from:
            filters.append(PersonModel.birth_year >= birth_year_from)
        if birth_year_to:
            filters.append(PersonModel.birth_year <= birth_year_to)
        if death_year_from:
            filters.append(PersonModel.death_year >= death_year_from)
        if death_year_to:
            filters.append(PersonModel.death_year <= death_year_to)
        if verification_status:
            filters.append(PersonModel.verification_status == verification_status)

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        # Get total count
        count_result = await self._session.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        query = query.order_by(PersonModel.full_name).limit(limit).offset(offset)
        result = await self._session.execute(query)
        models = result.scalars().all()

        return SearchResult(
            items=[self._to_entity(m) for m in models],
            total=total,
        )

    async def get_filter_values(self) -> FilterValues:
        """Получить доступные значения для фильтров."""
        # Get distinct regions
        regions_result = await self._session.execute(
            select(PersonModel.region)
            .distinct()
            .order_by(PersonModel.region)
        )
        regions = [r[0] for r in regions_result.fetchall()]

        # Get distinct accusation types (first word or phrase)
        accusations_result = await self._session.execute(
            select(PersonModel.accusation)
            .distinct()
            .order_by(PersonModel.accusation)
        )
        accusations = [a[0] for a in accusations_result.fetchall()]

        # Get year ranges
        years_result = await self._session.execute(
            select(
                func.min(PersonModel.birth_year),
                func.max(PersonModel.birth_year),
                func.min(PersonModel.death_year),
                func.max(PersonModel.death_year),
            )
        )
        row = years_result.fetchone()

        return FilterValues(
            regions=regions,
            accusation_types=accusations,
            min_birth_year=row[0] if row else None,
            max_birth_year=row[1] if row else None,
            min_death_year=row[2] if row else None,
            max_death_year=row[3] if row else None,
        )

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
            model.verification_status = person.verification_status.value
            model.verified_at = person.verified_at
            model.verified_by = person.verified_by
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

    async def get_pending_moderation(self, limit: int = 50, offset: int = 0) -> list[Person]:
        """Получить записи, ожидающие модерации."""
        from app.domain.value_objects import VerificationStatus
        
        result = await self._session.execute(
            select(PersonModel)
            .where(PersonModel.verification_status == VerificationStatus.PENDING.value)
            .order_by(PersonModel.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
