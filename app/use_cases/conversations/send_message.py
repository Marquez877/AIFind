from datetime import datetime
from uuid import UUID, uuid4

from app.domain.entities import Message, MessageRole
from app.domain.errors import ConversationNotFoundError
from app.providers import AIProvider, ConversationRepository


class SendMessageUseCase:
    def __init__(self, conv_repo: ConversationRepository, ai_provider: AIProvider) -> None:
        self._conv_repo = conv_repo
        self._ai_provider = ai_provider

    async def execute(self, conversation_id: UUID, user_message: str) -> Message:
        conversation = await self._conv_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        existing_messages = await self._conv_repo.get_messages(conversation_id)
        history = [{"role": msg.role.value, "content": msg.content} for msg in existing_messages]

        user_message_entity = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message,
            created_at=datetime.utcnow(),
        )
        await self._conv_repo.add_message(user_message_entity)

        assistant_text = await self._ai_provider.ask(history, user_message)
        assistant_message_entity = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=assistant_text,
            created_at=datetime.utcnow(),
        )
        return await self._conv_repo.add_message(assistant_message_entity)
