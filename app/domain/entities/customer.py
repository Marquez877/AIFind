from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from ..value_objects.email import Email


@dataclass(frozen=True)
class Customer:
    id: UUID
    name: str
    email: str  # use Email value object
    phone: str | None
    company: str | None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("Customer name cannot be empty")
        object.__setattr__(self, "name", normalized_name)

        validated_email = str(Email(self.email))
        object.__setattr__(self, "email", validated_email)

        if self.phone is not None:
            normalized_phone = self.phone.strip()
            object.__setattr__(self, "phone", normalized_phone or None)

        if self.company is not None:
            normalized_company = self.company.strip()
            object.__setattr__(self, "company", normalized_company or None)
