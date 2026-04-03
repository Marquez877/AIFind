from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Conversation:
    id: UUID
    customer_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        normalized_title = self.title.strip()
        if not normalized_title:
            raise ValueError("Conversation title cannot be empty")
        object.__setattr__(self, "title", normalized_title)
