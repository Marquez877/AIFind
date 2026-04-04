"""API router for person conversations with chat history."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_person_repo,
    get_document_repo,
    get_chunk_repo,
    get_embedding_service,
    get_claude_client,
)
from app.api.v1.schemas.person_conversation_schemas import (
    ChatWithHistoryRequest,
    PersonConversationCreate,
    PersonConversationDetailResponse,
    PersonConversationResponse,
    PersonMessageResponse,
)
from app.domain.errors import PersonNotFoundError
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.infrastructure.repositories.person_conversation_repository import PersonConversationRepository
from app.providers import AIProvider, DocumentRepository, PersonRepository
from app.use_cases.person_conversations import (
    ChatWithHistoryUseCase,
    CreatePersonConversationUseCase,
    DeletePersonConversationUseCase,
    GetPersonConversationUseCase,
    ListPersonConversationsUseCase,
)
from app.wiring import build_person_conversation_repository, get_session_dependency
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/persons/{person_id}/conversations", tags=["person-conversations"])


async def get_conversation_repo(
    session: AsyncSession = Depends(get_session_dependency),
) -> PersonConversationRepository:
    return build_person_conversation_repository(session)


@router.get("", response_model=list[PersonConversationResponse])
async def list_conversations(
    person_id: UUID,
    limit: int = 50,
    person_repo: PersonRepository = Depends(get_person_repo),
    conversation_repo: PersonConversationRepository = Depends(get_conversation_repo),
) -> list[PersonConversationResponse]:
    """Получить список диалогов по карточке."""
    use_case = ListPersonConversationsUseCase(person_repo, conversation_repo)
    try:
        conversations = await use_case.execute(person_id, limit=limit)
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    return [
        PersonConversationResponse(
            id=c.id,
            person_id=c.person_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=c.message_count,
        )
        for c in conversations
    ]


@router.post("", response_model=PersonConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    person_id: UUID,
    payload: PersonConversationCreate,
    person_repo: PersonRepository = Depends(get_person_repo),
    conversation_repo: PersonConversationRepository = Depends(get_conversation_repo),
) -> PersonConversationResponse:
    """Создать новый диалог по карточке."""
    use_case = CreatePersonConversationUseCase(person_repo, conversation_repo)
    try:
        conversation = await use_case.execute(person_id, title=payload.title)
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    return PersonConversationResponse(
        id=conversation.id,
        person_id=conversation.person_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0,
    )


@router.get("/{conversation_id}", response_model=PersonConversationDetailResponse)
async def get_conversation(
    person_id: UUID,
    conversation_id: UUID,
    conversation_repo: PersonConversationRepository = Depends(get_conversation_repo),
) -> PersonConversationDetailResponse:
    """Получить диалог со всеми сообщениями."""
    use_case = GetPersonConversationUseCase(conversation_repo)
    conversation = await use_case.execute(conversation_id)

    if conversation is None or conversation.person_id != person_id:
        raise HTTPException(status_code=404, detail="Диалог не найден")

    return PersonConversationDetailResponse(
        id=conversation.id,
        person_id=conversation.person_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            PersonMessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=m.sources,
                created_at=m.created_at,
            )
            for m in conversation.messages
        ],
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    person_id: UUID,
    conversation_id: UUID,
    conversation_repo: PersonConversationRepository = Depends(get_conversation_repo),
) -> None:
    """Удалить диалог."""
    # First check if conversation belongs to person
    conversation = await conversation_repo.get_by_id(conversation_id)
    if conversation is None or conversation.person_id != person_id:
        raise HTTPException(status_code=404, detail="Диалог не найден")

    use_case = DeletePersonConversationUseCase(conversation_repo)
    await use_case.execute(conversation_id)


@router.post("/{conversation_id}/chat", response_model=PersonMessageResponse)
async def chat_with_history(
    person_id: UUID,
    conversation_id: UUID,
    payload: ChatWithHistoryRequest,
    person_repo: PersonRepository = Depends(get_person_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    conversation_repo: PersonConversationRepository = Depends(get_conversation_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    ai_provider: AIProvider = Depends(get_claude_client),
) -> PersonMessageResponse:
    """Отправить сообщение в существующий диалог."""
    use_case = ChatWithHistoryUseCase(
        person_repo=person_repo,
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        conversation_repo=conversation_repo,
        embedding_service=embedding_service,
        ai_provider=ai_provider,
    )

    try:
        result = await use_case.execute(
            person_id=person_id,
            question=payload.question,
            conversation_id=conversation_id,
            use_semantic_search=False,
        )
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="Карточка не найдена")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return PersonMessageResponse(
        id=result.message.id,
        role=result.message.role,
        content=result.message.content,
        sources=result.message.sources,
        created_at=result.message.created_at,
    )


@router.post("/chat", response_model=PersonMessageResponse, status_code=status.HTTP_201_CREATED)
async def start_new_chat(
    person_id: UUID,
    payload: ChatWithHistoryRequest,
    person_repo: PersonRepository = Depends(get_person_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    conversation_repo: PersonConversationRepository = Depends(get_conversation_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    ai_provider: AIProvider = Depends(get_claude_client),
) -> PersonMessageResponse:
    """Начать новый диалог с первым вопросом.
    
    Создаёт новый диалог и возвращает ответ ассистента.
    Заголовок диалога формируется из первого вопроса.
    """
    use_case = ChatWithHistoryUseCase(
        person_repo=person_repo,
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        conversation_repo=conversation_repo,
        embedding_service=embedding_service,
        ai_provider=ai_provider,
    )

    try:
        result = await use_case.execute(
            person_id=person_id,
            question=payload.question,
            conversation_id=None,  # Creates new conversation
            use_semantic_search=False,
        )
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="Карточка не найдена")

    return PersonMessageResponse(
        id=result.message.id,
        role=result.message.role,
        content=result.message.content,
        sources=result.message.sources,
        created_at=result.message.created_at,
    )
