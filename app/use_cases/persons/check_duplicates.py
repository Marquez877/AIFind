from dataclasses import dataclass

from app.infrastructure.ai.embedding_service import EmbeddingService
from app.providers import DuplicateMatch, PersonRepository


@dataclass
class CheckDuplicatesResult:
    matches: list[DuplicateMatch]


class CheckPersonDuplicatesUseCase:
    """Use case для умного обнаружения дублей карточек."""

    def __init__(
        self,
        person_repo: PersonRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self._person_repo = person_repo
        self._embedding_service = embedding_service

    async def execute(
        self,
        full_name: str,
        birth_year: int,
        biography: str,
        limit: int = 5,
    ) -> CheckDuplicatesResult:
        biography_embedding = await self._embedding_service.get_embedding(biography)
        matches = await self._person_repo.find_potential_duplicates(
            full_name=full_name,
            birth_year=birth_year,
            biography_embedding=biography_embedding,
            limit=limit,
        )
        return CheckDuplicatesResult(matches=matches)
