from dataclasses import replace
from datetime import datetime
from uuid import UUID

from app.domain.entities import Customer
from app.domain.errors import CustomerAlreadyExistsError, CustomerNotFoundError
from app.domain.value_objects import Email
from app.providers import CustomerRepository


class UpdateCustomerUseCase:
    def __init__(self, repo: CustomerRepository) -> None:
        self._repo = repo

    async def execute(self, customer_id: UUID, **fields_to_update: object) -> Customer:
        customer = await self._repo.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)

        allowed_fields = {"name", "email", "phone", "company", "is_active"}
        unknown_fields = set(fields_to_update) - allowed_fields
        if unknown_fields:
            unknown_fields_list = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Unsupported fields to update: {unknown_fields_list}")

        updates: dict[str, object] = dict(fields_to_update)

        if "email" in updates:
            email_value = updates["email"]
            if email_value is None:
                raise ValueError("email cannot be None")

            normalized_email = str(Email(str(email_value)))
            existing_by_email = await self._repo.get_by_email(normalized_email)
            if existing_by_email is not None and existing_by_email.id != customer_id:
                raise CustomerAlreadyExistsError(normalized_email)
            updates["email"] = normalized_email

        updated_customer = replace(customer, **updates, updated_at=datetime.utcnow())
        return await self._repo.save(updated_customer)
