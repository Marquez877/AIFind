"""Use cases for managing person conversations."""

from uuid import UUID, uuid4

from app.domain.entities.person_conversation import PersonConversation
from app.domain.errors import PersonNotFoundError
from app.infrastructure.repositories.person_conversation_repository import PersonConversationRepository
from app.providers import PersonRepository


class CreatePersonConversationUseCase:
    """Create a new conversation for a person."""

    def __init__(
        self,
        person_repo: PersonRepository,
        conversation_repo: PersonConversationRepository,
    ) -> None:
        self._person_repo = person_repo
        self._conversation_repo = conversation_repo

    async def execute(self, person_id: UUID, title: str | None = None) -> PersonConversation:
        # Verify person exists
        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        conversation = PersonConversation(
            id=uuid4(),
            person_id=person_id,
            title=title or "Новый диалог",
        )
        return await self._conversation_repo.create(conversation)


class GetPersonConversationUseCase:
    """Get a conversation with all messages."""

    def __init__(self, conversation_repo: PersonConversationRepository) -> None:
        self._conversation_repo = conversation_repo

    async def execute(self, conversation_id: UUID) -> PersonConversation | None:
        return await self._conversation_repo.get_by_id(conversation_id)


class ListPersonConversationsUseCase:
    """List all conversations for a person."""

    def __init__(
        self,
        person_repo: PersonRepository,
        conversation_repo: PersonConversationRepository,
    ) -> None:
        self._person_repo = person_repo
        self._conversation_repo = conversation_repo

    async def execute(self, person_id: UUID, limit: int = 50) -> list[PersonConversation]:
        # Verify person exists
        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        return await self._conversation_repo.get_by_person_id(person_id, limit=limit)


class DeletePersonConversationUseCase:
    """Delete a conversation."""

    def __init__(self, conversation_repo: PersonConversationRepository) -> None:
        self._conversation_repo = conversation_repo

    async def execute(self, conversation_id: UUID) -> bool:
        return await self._conversation_repo.delete(conversation_id)
