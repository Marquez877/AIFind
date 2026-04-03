from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Conversation, Message


class ConversationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Conversation | None: ...

    @abstractmethod
    async def list_by_customer(self, customer_id: UUID) -> list[Conversation]: ...

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation: ...

    @abstractmethod
    async def add_message(self, message: Message) -> Message: ...

    @abstractmethod
    async def get_messages(self, conversation_id: UUID) -> list[Message]: ...
