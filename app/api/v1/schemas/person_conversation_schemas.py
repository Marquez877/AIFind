"""Schemas for person chat conversations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PersonMessageCreate(BaseModel):
    """Схема для отправки сообщения в диалог."""
    
    question: str = Field(..., min_length=1, max_length=2000, description="Вопрос пользователя")


class PersonMessageResponse(BaseModel):
    """Схема сообщения в диалоге."""
    
    id: UUID
    role: str = Field(description="user или assistant")
    content: str
    sources: list[dict] | None = Field(default=None, description="Источники (для ответов ассистента)")
    created_at: datetime


class PersonConversationCreate(BaseModel):
    """Схема для создания нового диалога."""
    
    title: str | None = Field(default=None, max_length=255, description="Заголовок диалога")


class PersonConversationResponse(BaseModel):
    """Схема диалога."""
    
    id: UUID
    person_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(default=0, description="Количество сообщений")


class PersonConversationDetailResponse(BaseModel):
    """Схема диалога с сообщениями."""
    
    id: UUID
    person_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[PersonMessageResponse]


class ChatWithHistoryRequest(BaseModel):
    """Запрос для чата с учётом истории диалога."""
    
    question: str = Field(..., min_length=1, max_length=2000)
