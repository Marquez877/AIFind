from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import UserRole


@dataclass(frozen=True)
class User:
    """Пользователь системы."""

    id: UUID
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        normalized_email = self.email.strip().lower()
        if not normalized_email:
            raise ValueError("Email cannot be empty")
        if "@" not in normalized_email:
            raise ValueError("Invalid email format")
        object.__setattr__(self, "email", normalized_email)

        if not self.password_hash:
            raise ValueError("Password hash cannot be empty")
