from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import VerificationStatus


@dataclass(frozen=True)
class Person:
    """Карточка репрессированного человека."""

    id: UUID
    full_name: str  # ФИО
    birth_year: int  # Год рождения
    death_year: int | None  # Год смерти (может быть неизвестен)
    region: str  # Регион
    accusation: str  # Обвинение
    biography: str  # Краткое описание/биография
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verified_at: datetime | None = None
    verified_by: str | None = None  # Email или ID модератора
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        normalized_name = self.full_name.strip()
        if not normalized_name:
            raise ValueError("Full name cannot be empty")
        object.__setattr__(self, "full_name", normalized_name)

        if self.birth_year < 1800 or self.birth_year > 1960:
            raise ValueError("Birth year must be between 1800 and 1960")

        if self.death_year is not None:
            if self.death_year < self.birth_year:
                raise ValueError("Death year cannot be before birth year")
            if self.death_year > 1960:
                raise ValueError("Death year must be before 1960")

        normalized_region = self.region.strip()
        if not normalized_region:
            raise ValueError("Region cannot be empty")
        object.__setattr__(self, "region", normalized_region)

        normalized_accusation = self.accusation.strip()
        if not normalized_accusation:
            raise ValueError("Accusation cannot be empty")
        object.__setattr__(self, "accusation", normalized_accusation)

        normalized_biography = self.biography.strip()
        if not normalized_biography:
            raise ValueError("Biography cannot be empty")
        object.__setattr__(self, "biography", normalized_biography)
