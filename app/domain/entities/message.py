from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class Message:
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime

    def __post_init__(self) -> None:
        if isinstance(self.role, str):
            object.__setattr__(self, "role", MessageRole(self.role))

        normalized_content = self.content.strip()
        if not normalized_content:
            raise ValueError("Message content cannot be empty")
        object.__setattr__(self, "content", normalized_content)
