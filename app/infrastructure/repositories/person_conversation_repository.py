"""Repository for person conversations with chat history."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.person_conversation import PersonConversation, PersonMessage
from app.infrastructure.db.models import PersonConversationModel, PersonMessageModel


class PersonConversationRepository:
    """Repository for storing and retrieving person chat conversations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _message_to_entity(model: PersonMessageModel) -> PersonMessage:
        return PersonMessage(
            id=model.id,
            conversation_id=model.conversation_id,
            role=model.role,
            content=model.content,
            sources=model.sources,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_entity(model: PersonConversationModel, include_messages: bool = False) -> PersonConversation:
        messages = []
        if include_messages and model.messages:
            messages = [
                PersonConversationRepository._message_to_entity(m)
                for m in model.messages
            ]
        
        return PersonConversation(
            id=model.id,
            person_id=model.person_id,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=messages,
        )

    async def create(self, conversation: PersonConversation) -> PersonConversation:
        """Create a new conversation."""
        model = PersonConversationModel(
            id=conversation.id,
            person_id=conversation.person_id,
            title=conversation.title,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, conversation_id: UUID) -> PersonConversation | None:
        """Get conversation by ID with all messages."""
        result = await self._session.execute(
            select(PersonConversationModel)
            .options(selectinload(PersonConversationModel.messages))
            .where(PersonConversationModel.id == conversation_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model, include_messages=True)

    async def get_by_person_id(self, person_id: UUID, limit: int = 50) -> list[PersonConversation]:
        """Get all conversations for a person."""
        result = await self._session.execute(
            select(PersonConversationModel)
            .where(PersonConversationModel.person_id == person_id)
            .order_by(PersonConversationModel.updated_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def add_message(self, message: PersonMessage) -> PersonMessage:
        """Add a message to a conversation."""
        model = PersonMessageModel(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            sources=message.sources,
        )
        self._session.add(model)
        
        # Update conversation's updated_at
        await self._session.execute(
            select(PersonConversationModel)
            .where(PersonConversationModel.id == message.conversation_id)
        )
        
        await self._session.commit()
        await self._session.refresh(model)
        return self._message_to_entity(model)

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int | None = None,
    ) -> list[PersonMessage]:
        """Get messages for a conversation."""
        query = (
            select(PersonMessageModel)
            .where(PersonMessageModel.conversation_id == conversation_id)
            .order_by(PersonMessageModel.created_at)
        )
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._message_to_entity(m) for m in models]

    async def get_recent_messages(
        self,
        conversation_id: UUID,
        limit: int = 10,
    ) -> list[PersonMessage]:
        """Get most recent messages for context."""
        # Get last N messages in reverse order, then reverse to get chronological order
        query = (
            select(PersonMessageModel)
            .where(PersonMessageModel.conversation_id == conversation_id)
            .order_by(PersonMessageModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        models = list(result.scalars().all())
        models.reverse()  # Restore chronological order
        return [self._message_to_entity(m) for m in models]

    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation and all its messages."""
        result = await self._session.execute(
            select(PersonConversationModel)
            .where(PersonConversationModel.id == conversation_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def count_by_person_id(self, person_id: UUID) -> int:
        """Count conversations for a person."""
        result = await self._session.execute(
            select(func.count(PersonConversationModel.id))
            .where(PersonConversationModel.person_id == person_id)
        )
        return result.scalar() or 0
