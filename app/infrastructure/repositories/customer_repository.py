from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Customer
from app.infrastructure.db.models import CustomerModel
from app.providers import CustomerRepository


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: CustomerModel) -> Customer:
        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            company=model.company,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: Customer) -> CustomerModel:
        return CustomerModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            company=entity.company,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Customer | None:
        result = await self._session.execute(select(CustomerModel).where(CustomerModel.id == id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_email(self, email: str) -> Customer | None:
        result = await self._session.execute(select(CustomerModel).where(CustomerModel.email == email))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list(
        self,
        name: str | None,
        email: str | None,
        company: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[Customer]:
        query = select(CustomerModel)

        if name is not None:
            query = query.where(CustomerModel.name.ilike(f"%{name}%"))
        if email is not None:
            query = query.where(CustomerModel.email.ilike(f"%{email}%"))
        if company is not None:
            query = query.where(CustomerModel.company.ilike(f"%{company}%"))
        if is_active is not None:
            query = query.where(CustomerModel.is_active.is_(is_active))

        query = query.limit(limit).offset(offset)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def save(self, customer: Customer) -> Customer:
        existing_result = await self._session.execute(select(CustomerModel).where(CustomerModel.id == customer.id))
        model = existing_result.scalar_one_or_none()

        if model is None:
            model = self._to_model(customer)
            self._session.add(model)
        else:
            model.name = customer.name
            model.email = customer.email
            model.phone = customer.phone
            model.company = customer.company
            model.is_active = customer.is_active
            model.created_at = customer.created_at
            model.updated_at = customer.updated_at

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        result = await self._session.execute(select(CustomerModel).where(CustomerModel.id == id))
        model = result.scalar_one_or_none()
        if model is None:
            return

        model.is_active = False
        model.updated_at = datetime.utcnow()

        await self._session.commit()
