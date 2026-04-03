from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Customer


class CustomerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Customer | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Customer | None: ...

    @abstractmethod
    async def list(
        self,
        name: str | None,
        email: str | None,
        company: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[Customer]: ...

    @abstractmethod
    async def save(self, customer: Customer) -> Customer: ...

    @abstractmethod
    async def delete(self, id: UUID) -> None: ...
