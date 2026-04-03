from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.dependencies import (
    get_create_person_uc,
    get_delete_person_uc,
    get_get_person_uc,
    get_list_persons_uc,
    get_update_person_uc,
)
from app.api.v1.schemas import PersonCreateRequest, PersonResponse, PersonUpdateRequest
from app.domain.errors import PersonAlreadyExistsError, PersonNotFoundError
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


@router.get("", response_model=list[PersonResponse])
async def list_persons(
    name: str | None = Query(default=None, description="Поиск по имени"),
    region: str | None = Query(default=None, description="Фильтр по региону"),
    accusation: str | None = Query(default=None, description="Фильтр по обвинению"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    use_case: ListPersonsUseCase = Depends(get_list_persons_uc),
) -> list[PersonResponse]:
    """Получить список карточек с фильтрацией."""
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
