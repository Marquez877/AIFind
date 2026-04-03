from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Схема запроса для чата с ИИ."""

    question: str = Field(..., min_length=1, max_length=2000, description="Вопрос пользователя")
    use_semantic_search: bool = Field(default=True, description="Использовать семантический поиск")
    top_k: int = Field(default=3, ge=1, le=10, description="Количество релевантных чанков")


class SourceReferenceResponse(BaseModel):
    """Ссылка на источник."""

    document_id: UUID
    document_name: str
    chunk_text: str = Field(description="Фрагмент текста из документа")
    relevance_score: float = Field(ge=0, le=1, description="Оценка релевантности (0-1)")


class ChatResponse(BaseModel):
    """Схема ответа от ИИ-ассистента."""

    answer: str = Field(..., description="Ответ на основе документов")
    sources: list[str] = Field(default_factory=list, description="Список использованных документов")


class SemanticChatResponse(BaseModel):
    """Расширенный ответ с детальными источниками."""

    answer: str = Field(..., description="Ответ на основе документов")
    sources: list[SourceReferenceResponse] = Field(
        default_factory=list,
        description="Детальные ссылки на источники",
    )
