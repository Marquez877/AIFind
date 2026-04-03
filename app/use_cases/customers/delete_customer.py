from uuid import UUID

from app.domain.errors import CustomerNotFoundError
from app.providers import CustomerRepository


class DeleteCustomerUseCase:
    def __init__(self, repo: CustomerRepository) -> None:
        self._repo = repo

    async def execute(self, customer_id: UUID) -> None:
        customer = await self._repo.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        await self._repo.delete(customer_id)
