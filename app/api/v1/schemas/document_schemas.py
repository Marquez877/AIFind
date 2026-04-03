from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Схема ответа с данными документа."""

    id: UUID
    person_id: UUID
    filename: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentContentResponse(BaseModel):
    """Схема ответа с содержимым документа."""

    id: UUID
    person_id: UUID
    filename: str
    content: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
