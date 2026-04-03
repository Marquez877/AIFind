from dataclasses import replace
from datetime import datetime
from uuid import UUID

from app.domain.entities import Person
from app.domain.errors import PersonNotFoundError
from app.domain.value_objects import VerificationStatus
from app.providers import PersonRepository


class VerifyPersonUseCase:
    """Use case для верификации карточки репрессированного."""

    def __init__(self, person_repo: PersonRepository) -> None:
        self._person_repo = person_repo

    async def execute(
        self,
        person_id: UUID,
        status: VerificationStatus,
        verified_by: str,
    ) -> Person:
        """Изменить статус верификации карточки.
        
        Args:
            person_id: ID карточки
            status: Новый статус (verified или rejected)
            verified_by: Email или ID модератора
        
        Returns:
            Обновленная карточка
        
        Raises:
            PersonNotFoundError: Если карточка не найдена
        """
        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        # Обновить статус верификации
        updated_person = replace(
            person,
            verification_status=status,
            verified_at=datetime.utcnow(),
            verified_by=verified_by,
            updated_at=datetime.utcnow(),
        )

        return await self._person_repo.save(updated_person)
