"""Domain entities for person conversations."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class PersonMessage:
    """Сообщение в диалоге по карточке."""
    
    id: UUID
    conversation_id: UUID
    role: str  # 'user' or 'assistant'
    content: str
    sources: list[dict] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PersonConversation:
    """Диалог по карточке репрессированного."""
    
    id: UUID
    person_id: UUID
    title: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    messages: list[PersonMessage] = field(default_factory=list)

    @property
    def message_count(self) -> int:
        return len(self.messages)
