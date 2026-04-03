from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Схема запроса для чата с ИИ."""

    question: str = Field(..., min_length=1, max_length=2000, description="Вопрос пользователя")


class ChatResponse(BaseModel):
    """Схема ответа от ИИ-ассистента."""

    answer: str = Field(..., description="Ответ на основе документов")
    sources: list[str] = Field(default_factory=list, description="Список использованных документов")
