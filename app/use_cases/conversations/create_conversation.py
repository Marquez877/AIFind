from datetime import datetime
from uuid import UUID, uuid4

from app.domain.entities import Conversation
from app.domain.errors import CustomerNotFoundError
from app.providers import ConversationRepository, CustomerRepository


class CreateConversationUseCase:
    def __init__(self, customer_repo: CustomerRepository, conv_repo: ConversationRepository) -> None:
        self._customer_repo = customer_repo
        self._conv_repo = conv_repo

    async def execute(self, customer_id: UUID, title: str) -> Conversation:
        customer = await self._customer_repo.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)

        now = datetime.utcnow()
        conversation = Conversation(
            id=uuid4(),
            customer_id=customer_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        return await self._conv_repo.save(conversation)
