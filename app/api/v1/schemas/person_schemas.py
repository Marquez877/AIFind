from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PersonCreateRequest(BaseModel):
    """Схема запроса на создание карточки репрессированного."""

    full_name: str = Field(..., min_length=1, max_length=255, description="ФИО")
    birth_year: int = Field(..., ge=1800, le=1960, description="Год рождения")
    death_year: int | None = Field(None, ge=1800, le=1960, description="Год смерти")
    region: str = Field(..., min_length=1, max_length=255, description="Регион")
    accusation: str = Field(..., min_length=1, max_length=500, description="Обвинение")
    biography: str = Field(..., min_length=1, description="Биография")


class PersonUpdateRequest(BaseModel):
    """Схема запроса на обновление карточки."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    birth_year: int | None = Field(None, ge=1800, le=1960)
    death_year: int | None = Field(None, ge=1800, le=1960)
    region: str | None = Field(None, min_length=1, max_length=255)
    accusation: str | None = Field(None, min_length=1, max_length=500)
    biography: str | None = Field(None, min_length=1)


class PersonResponse(BaseModel):
    """Схема ответа с данными карточки."""

    id: UUID
    full_name: str
    birth_year: int
    death_year: int | None
    region: str
    accusation: str
    biography: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
