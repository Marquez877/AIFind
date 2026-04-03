from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette import EventSourceResponse

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


@router.get("/chat/stream")
async def ask_question_semantic_stream(
    person_id: UUID,
    question: str,
    top_k: int = 3,
    use_case: SemanticSearchUseCase = Depends(get_semantic_search_uc),
) -> EventSourceResponse:
    """SSE-стриминг ответа с семантическим поиском по документам."""
    if not question.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="question must not be empty",
        )
    if top_k < 1 or top_k > 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="top_k must be between 1 and 10",
        )

    async def event_generator():
        try:
            prepared = await use_case.prepare_context(
                person_id=person_id,
                question=question,
                top_k=top_k,
            )

            if prepared.immediate_answer is not None:
                for token in prepared.immediate_answer:
                    yield {"event": "token", "data": token}
                yield {"event": "sources", "data": []}
                yield {"event": "done", "data": "ok"}
                return

            async for token in use_case.stream_answer(prepared, question):
                yield {"event": "token", "data": token}

            sources_payload = [
                {
                    "document_id": str(src.document_id),
                    "document_name": src.document_name,
                    "chunk_text": src.chunk_text,
                    "relevance_score": src.relevance_score,
                }
                for src in prepared.sources
            ]
            yield {"event": "sources", "data": json.dumps(sources_payload, ensure_ascii=False)}
            yield {"event": "done", "data": "ok"}
        except PersonNotFoundError:
            yield {"event": "error", "data": "Карточка не найдена"}
        except RuntimeError as exc:
            yield {"event": "error", "data": str(exc)}

    return EventSourceResponse(event_generator())
