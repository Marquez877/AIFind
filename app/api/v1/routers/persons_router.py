from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_user,
    get_create_person_uc,
    get_delete_person_uc,
    get_get_person_uc,
    get_list_persons_uc,
    get_update_person_uc,
    get_person_repo,
)
from app.api.v1.schemas import (
    FiltersResponse,
    PersonCreateRequest,
    PersonResponse,
    PersonSearchResponse,
    PersonUpdateRequest,
)
from app.domain.entities import User
from app.domain.errors import PersonAlreadyExistsError, PersonNotFoundError
from app.infrastructure.repositories.person_repository import SQLAlchemyPersonRepository
from app.providers import PersonRepository
from app.use_cases.persons import (
    CreatePersonUseCase,
    DeletePersonUseCase,
    GetPersonUseCase,
    ListPersonsUseCase,
    UpdatePersonUseCase,
)


router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    payload: PersonCreateRequest,
    use_case: CreatePersonUseCase = Depends(get_create_person_uc),
    current_user: User = Depends(get_current_user),
) -> PersonResponse:
    """Создать карточку репрессированного."""
    try:
        person = await use_case.execute(
            full_name=payload.full_name,
            birth_year=payload.birth_year,
            death_year=payload.death_year,
            region=payload.region,
            accusation=payload.accusation,
            biography=payload.biography,
        )
    except PersonAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Запись с таким именем и годом рождения уже существует (ID: {exc.existing_id})",
        ) from exc

    return PersonResponse.model_validate(person)


@router.get("/search", response_model=PersonSearchResponse)
async def search_persons(
    name: str | None = Query(default=None, description="Поиск по имени (частичное совпадение)"),
    region: str | None = Query(default=None, description="Фильтр по региону"),
    accusation_type: str | None = Query(default=None, description="Тип обвинения (частичное совпадение)"),
    birth_year_from: int | None = Query(default=None, ge=1800, le=1960, description="Год рождения от"),
    birth_year_to: int | None = Query(default=None, ge=1800, le=1960, description="Год рождения до"),
    death_year_from: int | None = Query(default=None, ge=1800, le=1960, description="Год смерти от"),
    death_year_to: int | None = Query(default=None, ge=1800, le=1960, description="Год смерти до"),
    verification_status: str | None = Query(default=None, pattern="^(pending|verified|rejected)$", description="Статус верификации"),
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    page_size: int = Query(default=20, ge=1, le=100, description="Размер страницы"),
    person_repo: PersonRepository = Depends(get_person_repo),
) -> PersonSearchResponse:
    """Расширенный поиск по карточкам с пагинацией и фильтром по статусу верификации."""
    offset = (page - 1) * page_size
    
    result = await person_repo.search(
        name=name,
        region=region,
        accusation_type=accusation_type,
        birth_year_from=birth_year_from,
        birth_year_to=birth_year_to,
        death_year_from=death_year_from,
        death_year_to=death_year_to,
        verification_status=verification_status,
        limit=page_size,
        offset=offset,
    )
    
    total_pages = ceil(result.total / page_size) if result.total > 0 else 0
    
    return PersonSearchResponse(
        items=[PersonResponse.model_validate(person) for person in result.items],
        total=result.total,
        page=page,
        page_size=page_size,
        pages=total_pages,
    )


@router.get("", response_model=list[PersonResponse])
async def list_persons(
    name: str | None = Query(default=None, description="Поиск по имени"),
    region: str | None = Query(default=None, description="Фильтр по региону"),
    accusation: str | None = Query(default=None, description="Фильтр по обвинению"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    use_case: ListPersonsUseCase = Depends(get_list_persons_uc),
) -> list[PersonResponse]:
    """Получить список карточек с фильтрацией (упрощённый)."""
    persons = await use_case.execute(name, region, accusation, limit, offset)
    return [PersonResponse.model_validate(person) for person in persons]


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: UUID,
    use_case: GetPersonUseCase = Depends(get_get_person_uc),
) -> PersonResponse:
    """Получить карточку по ID."""
    try:
        person = await use_case.execute(person_id)
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return PersonResponse.model_validate(person)


@router.patch("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: UUID,
    payload: PersonUpdateRequest,
    use_case: UpdatePersonUseCase = Depends(get_update_person_uc),
    current_user: User = Depends(get_current_user),
) -> PersonResponse:
    """Обновить карточку."""
    updates = payload.model_dump(exclude_unset=True)

    try:
        person = await use_case.execute(person_id, **updates)
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc
    except PersonAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Запись с таким именем и годом рождения уже существует (ID: {exc.existing_id})",
        ) from exc

    return PersonResponse.model_validate(person)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: UUID,
    use_case: DeletePersonUseCase = Depends(get_delete_person_uc),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Удалить карточку."""
    try:
        await use_case.execute(person_id)
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
