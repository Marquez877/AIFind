from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_person_repo, require_role
from app.api.v1.schemas import PersonResponse, VerifyPersonRequest
from app.domain.entities import User
from app.domain.errors import PersonNotFoundError
from app.domain.value_objects import VerificationStatus
from app.providers import PersonRepository
from app.use_cases.persons import GetPendingModerationUseCase, VerifyPersonUseCase


router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/pending", response_model=list[PersonResponse])
async def get_pending_moderation(
    limit: int = Query(default=50, ge=1, le=100, description="Количество записей"),
    offset: int = Query(default=0, ge=0, description="Смещение"),
    person_repo: PersonRepository = Depends(get_person_repo),
    current_user: User = Depends(require_role("moderator", "admin")),
) -> list[PersonResponse]:
    """Получить список карточек, ожидающих модерации (статус pending)."""
    use_case = GetPendingModerationUseCase(person_repo)
    persons = await use_case.execute(limit, offset)
    return [PersonResponse.model_validate(person) for person in persons]


@router.patch("/persons/{person_id}/verify", response_model=PersonResponse)
async def verify_person(
    person_id: UUID,
    payload: VerifyPersonRequest,
    person_repo: PersonRepository = Depends(get_person_repo),
    current_user: User = Depends(require_role("moderator", "admin")),
) -> PersonResponse:
    """Изменить статус верификации карточки.
    
    Доступные статусы: verified, rejected.
    """
    try:
        status_enum = VerificationStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый статус: {payload.status}",
        ) from exc

    use_case = VerifyPersonUseCase(person_repo)
    
    try:
        person = await use_case.execute(
            person_id=person_id,
            status=status_enum,
            verified_by=payload.verified_by,
        )
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return PersonResponse.model_validate(person)
