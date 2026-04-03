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
    verification_status: str
    verified_at: datetime | None = None
    verified_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerifyPersonRequest(BaseModel):
    """Схема запроса на верификацию карточки."""

    status: str = Field(..., pattern="^(verified|rejected)$", description="Статус: verified или rejected")
    verified_by: str = Field(..., min_length=1, max_length=255, description="Email или ID модератора")


class PersonSearchParams(BaseModel):
    """Параметры расширенного поиска по карточкам."""

    name: str | None = Field(None, description="Поиск по имени (частичное совпадение)")
    region: str | None = Field(None, description="Фильтр по региону")
    birth_year_from: int | None = Field(None, ge=1800, le=1960, description="Год рождения от")
    birth_year_to: int | None = Field(None, ge=1800, le=1960, description="Год рождения до")
    death_year_from: int | None = Field(None, ge=1800, le=1960, description="Год смерти от")
    death_year_to: int | None = Field(None, ge=1800, le=1960, description="Год смерти до")
    accusation_type: str | None = Field(None, description="Тип обвинения (частичное совпадение)")


class PersonSearchResponse(BaseModel):
    """Результат поиска с пагинацией."""

    items: list[PersonResponse]
    total: int = Field(description="Общее количество найденных записей")
    page: int = Field(description="Текущая страница")
    page_size: int = Field(description="Размер страницы")
    pages: int = Field(description="Всего страниц")


class FiltersResponse(BaseModel):
    """Доступные значения фильтров."""

    regions: list[str] = Field(description="Список всех регионов")
    accusation_types: list[str] = Field(description="Список типов обвинений")
    year_range: dict = Field(description="Диапазон годов {min_birth, max_birth, min_death, max_death}")
