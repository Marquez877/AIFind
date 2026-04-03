from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_ask_question_uc, get_semantic_search_uc
from app.api.v1.schemas import ChatRequest, ChatResponse, SemanticChatResponse, SourceReferenceResponse
from app.domain.errors import PersonNotFoundError
from app.use_cases.rag import AskQuestionUseCase
from app.use_cases.rag.semantic_search import SemanticSearchUseCase


router = APIRouter(tags=["chat"])


@router.post("/persons/{person_id}/chat", response_model=ChatResponse)
async def ask_question(
    person_id: UUID,
    payload: ChatRequest,
    use_case: AskQuestionUseCase = Depends(get_ask_question_uc),
) -> ChatResponse:
    """Задать вопрос ИИ-ассистенту на основе документов карточки (базовый RAG)."""
    try:
        result = await use_case.execute(person_id, payload.question)
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return ChatResponse(answer=result.answer, sources=result.sources)


@router.post("/persons/{person_id}/chat/semantic", response_model=SemanticChatResponse)
async def ask_question_semantic(
    person_id: UUID,
    payload: ChatRequest,
    use_case: SemanticSearchUseCase = Depends(get_semantic_search_uc),
) -> SemanticChatResponse:
    """Задать вопрос с семантическим поиском по документам (продвинутый RAG).
    
    Использует векторные эмбеддинги для поиска наиболее релевантных
    фрагментов документов перед отправкой в LLM.
    """
    try:
        result = await use_case.execute(
            person_id=person_id,
            question=payload.question,
            top_k=payload.top_k,
        )
    except PersonNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карточка не найдена",
        ) from exc

    return SemanticChatResponse(
        answer=result.answer,
        sources=[
            SourceReferenceResponse(
                document_id=src.document_id,
                document_name=src.document_name,
                chunk_text=src.chunk_text,
                relevance_score=src.relevance_score,
            )
            for src in result.sources
        ],
    )
