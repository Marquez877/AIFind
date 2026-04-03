from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Conversation, Message, MessageRole
from app.infrastructure.db.models import ConversationModel, MessageModel
from app.providers import ConversationRepository


class SQLAlchemyConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_conversation_entity(model: ConversationModel) -> Conversation:
        return Conversation(
            id=model.id,
            customer_id=model.customer_id,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_message_entity(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            conversation_id=model.conversation_id,
            role=MessageRole(model.role),
            content=model.content,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_conversation_model(entity: Conversation) -> ConversationModel:
        return ConversationModel(
            id=entity.id,
            customer_id=entity.customer_id,
            title=entity.title,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _to_message_model(entity: Message) -> MessageModel:
        return MessageModel(
            id=entity.id,
            conversation_id=entity.conversation_id,
            role=entity.role.value,
            content=entity.content,
            created_at=entity.created_at,
        )

    async def get_by_id(self, id: UUID) -> Conversation | None:
        result = await self._session.execute(select(ConversationModel).where(ConversationModel.id == id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_conversation_entity(model)

    async def list_by_customer(self, customer_id: UUID) -> list[Conversation]:
        result = await self._session.execute(
            select(ConversationModel)
            .where(ConversationModel.customer_id == customer_id)
            .order_by(ConversationModel.created_at.asc())
        )
        models = result.scalars().all()
        return [self._to_conversation_entity(model) for model in models]

    async def save(self, conversation: Conversation) -> Conversation:
        existing_result = await self._session.execute(
            select(ConversationModel).where(ConversationModel.id == conversation.id)
        )
        model = existing_result.scalar_one_or_none()

        if model is None:
            model = self._to_conversation_model(conversation)
            self._session.add(model)
        else:
            model.customer_id = conversation.customer_id
            model.title = conversation.title
            model.created_at = conversation.created_at
            model.updated_at = conversation.updated_at

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_conversation_entity(model)

    async def add_message(self, message: Message) -> Message:
        model = self._to_message_model(message)
        self._session.add(model)

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_message_entity(model)

    async def get_messages(self, conversation_id: UUID) -> list[Message]:
        result = await self._session.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
        )
        models = result.scalars().all()
        return [self._to_message_entity(model) for model in models]
