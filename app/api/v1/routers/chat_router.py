from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_ask_question_uc
from app.api.v1.schemas import ChatRequest, ChatResponse
from app.domain.errors import PersonNotFoundError
from app.use_cases.rag import AskQuestionUseCase


router = APIRouter(tags=["chat"])


@router.post("/persons/{person_id}/chat", response_model=ChatResponse)
async def ask_question(
    person_id: UUID,
    payload: ChatRequest,
    use_case: AskQuestionUseCase = Depends(get_ask_question_uc),
) -> ChatResponse:
    """Задать вопрос ИИ-ассистенту на основе документов карточки."""
    try:
        result = await use_case.execute(person_id, payload.question)
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return ChatResponse(answer=result.answer, sources=result.sources)
