from fastapi import APIRouter, Depends

from app.api.dependencies import get_person_repo
from app.api.v1.schemas import FiltersResponse
from app.providers import PersonRepository


router = APIRouter(prefix="/filters", tags=["filters"])


@router.get("", response_model=FiltersResponse)
async def get_filters(
    person_repo: PersonRepository = Depends(get_person_repo),
) -> FiltersResponse:
    """Получить доступные значения для фильтров поиска.
    
    Возвращает список всех регионов, типов обвинений и диапазон годов.
    """
    filter_values = await person_repo.get_filter_values()
    
    return FiltersResponse(
        regions=filter_values.regions,
        accusation_types=filter_values.accusation_types,
        year_range={
            "min_birth": filter_values.min_birth_year,
            "max_birth": filter_values.max_birth_year,
            "min_death": filter_values.min_death_year,
            "max_death": filter_values.max_death_year,
        },
    )
