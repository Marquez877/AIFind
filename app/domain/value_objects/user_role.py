from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей в системе."""

    USER = "user"  # Обычный пользователь (может создавать карточки)
    MODERATOR = "moderator"  # Модератор (может верифицировать карточки)
    ADMIN = "admin"  # Администратор (полный доступ)

    def __str__(self) -> str:
        return self.value
