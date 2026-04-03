from app.domain.entities import Customer
from app.domain.errors import CustomerAlreadyExistsError
from app.domain.value_objects import CustomerId, Email
from app.providers import CustomerRepository


class CreateCustomerUseCase:
    def __init__(self, repo: CustomerRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        name: str,
        email: str,
        phone: str | None,
        company: str | None,
    ) -> Customer:
        normalized_email = str(Email(email))
        existing_customer = await self._repo.get_by_email(normalized_email)
        if existing_customer is not None:
            raise CustomerAlreadyExistsError(normalized_email)

        customer = Customer(
            id=CustomerId.generate().value,
            name=name,
            email=normalized_email,
            phone=phone,
            company=company,
        )
        return await self._repo.save(customer)
