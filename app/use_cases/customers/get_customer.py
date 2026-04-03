from uuid import UUID

from app.domain.entities import Customer
from app.domain.errors import CustomerNotFoundError
from app.providers import CustomerRepository


class GetCustomerUseCase:
    def __init__(self, repo: CustomerRepository) -> None:
        self._repo = repo

    async def execute(self, customer_id: UUID) -> Customer:
        customer = await self._repo.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer
