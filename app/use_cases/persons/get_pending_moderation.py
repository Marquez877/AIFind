from app.providers import PersonRepository


class GetPendingModerationUseCase:
    """Use case для получения карточек, ожидающих модерации."""

    def __init__(self, person_repo: PersonRepository) -> None:
        self._person_repo = person_repo

    async def execute(self, limit: int = 50, offset: int = 0):
        """Получить список карточек в статусе pending."""
        return await self._person_repo.get_pending_moderation(limit, offset)
