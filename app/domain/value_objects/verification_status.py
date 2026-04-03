from enum import Enum


class VerificationStatus(str, Enum):
    """Статус верификации карточки репрессированного."""

    PENDING = "pending"  # Ожидает проверки
    VERIFIED = "verified"  # Верифицирована
    REJECTED = "rejected"  # Отклонена

    def __str__(self) -> str:
        return self.value
