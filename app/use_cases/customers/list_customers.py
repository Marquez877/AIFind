from app.domain.entities import Customer
from app.providers import CustomerRepository


class ListCustomersUseCase:
    def __init__(self, repo: CustomerRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        name: str | None,
        email: str | None,
        company: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[Customer]:
        return await self._repo.list(name, email, company, is_active, limit, offset)
