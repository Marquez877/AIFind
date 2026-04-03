from uuid import UUID


class CustomerNotFoundError(Exception):
    def __init__(self, customer_id: UUID) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer not found: {customer_id}")


class CustomerAlreadyExistsError(Exception):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Customer already exists: {email}")
