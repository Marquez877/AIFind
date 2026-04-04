from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.auth import JWTHandler
from app.infrastructure.parsers import ParserFactory
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.storage import LocalDocumentStorage
from app.providers import AIProvider, DocumentRepository, PersonRepository
from app.use_cases.documents import (
    DeleteDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    UploadDocumentUseCase,
)
from app.use_cases.persons import (
    CheckPersonDuplicatesUseCase,
    CreatePersonUseCase,
    DeletePersonUseCase,
    GetPersonUseCase,
    ListPersonsUseCase,
    UpdatePersonUseCase,
)
from app.use_cases.rag import AskQuestionUseCase
from app.use_cases.rag.semantic_search import SemanticSearchUseCase
from app.wiring import (
    build_ai_provider,
    build_chunk_repository,
    build_document_repository,
    build_document_storage,
    build_embedding_service,
    build_person_repository,
    build_user_repository,
    get_session_dependency,
)

# ─────────────────────────────────────────────────────────────────────────────
# Singletons
# ─────────────────────────────────────────────────────────────────────────────

_parser_factory = ParserFactory()


def get_parser_factory() -> ParserFactory:
    return _parser_factory


def get_document_storage() -> LocalDocumentStorage:
    return build_document_storage()


# ─────────────────────────────────────────────────────────────────────────────
# Repositories
# ─────────────────────────────────────────────────────────────────────────────

async def get_person_repo(session: AsyncSession = Depends(get_session_dependency)) -> PersonRepository:
    return build_person_repository(session)


async def get_document_repo(session: AsyncSession = Depends(get_session_dependency)) -> DocumentRepository:
    return build_document_repository(session)


async def get_chunk_repo(session: AsyncSession = Depends(get_session_dependency)) -> ChunkRepository:
    return build_chunk_repository(session)


async def get_user_repo(session: AsyncSession = Depends(get_session_dependency)) -> UserRepository:
    return build_user_repository(session)


async def get_embedding_service() -> EmbeddingService:
    return build_embedding_service()


async def get_claude_client() -> AIProvider:
    return build_ai_provider()


# ─────────────────────────────────────────────────────────────────────────────
# Person Use Cases
# ─────────────────────────────────────────────────────────────────────────────

async def get_create_person_uc(
    repo: PersonRepository = Depends(get_person_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> CreatePersonUseCase:
    return CreatePersonUseCase(repo, embedding_service)


async def get_get_person_uc(repo: PersonRepository = Depends(get_person_repo)) -> GetPersonUseCase:
    return GetPersonUseCase(repo)


async def get_list_persons_uc(repo: PersonRepository = Depends(get_person_repo)) -> ListPersonsUseCase:
    return ListPersonsUseCase(repo)


async def get_update_person_uc(
    repo: PersonRepository = Depends(get_person_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> UpdatePersonUseCase:
    return UpdatePersonUseCase(repo, embedding_service)


async def get_check_person_duplicates_uc(
    repo: PersonRepository = Depends(get_person_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> CheckPersonDuplicatesUseCase:
    return CheckPersonDuplicatesUseCase(repo, embedding_service)


async def get_delete_person_uc(repo: PersonRepository = Depends(get_person_repo)) -> DeletePersonUseCase:
    return DeletePersonUseCase(repo)


# ─────────────────────────────────────────────────────────────────────────────
# Document Use Cases
# ─────────────────────────────────────────────────────────────────────────────

async def get_upload_document_uc(
    person_repo: PersonRepository = Depends(get_person_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    parser_factory: ParserFactory = Depends(get_parser_factory),
    document_storage: LocalDocumentStorage = Depends(get_document_storage),
) -> UploadDocumentUseCase:
    return UploadDocumentUseCase(
        person_repo, document_repo, chunk_repo, embedding_service, parser_factory, document_storage
    )


async def get_list_documents_uc(
    person_repo: PersonRepository = Depends(get_person_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> ListDocumentsUseCase:
    return ListDocumentsUseCase(person_repo, document_repo)


async def get_get_document_uc(document_repo: DocumentRepository = Depends(get_document_repo)) -> GetDocumentUseCase:
    return GetDocumentUseCase(document_repo)


async def get_delete_document_uc(
    document_repo: DocumentRepository = Depends(get_document_repo),
    document_storage: LocalDocumentStorage = Depends(get_document_storage),
) -> DeleteDocumentUseCase:
    return DeleteDocumentUseCase(document_repo, document_storage)


# ─────────────────────────────────────────────────────────────────────────────
# RAG Use Cases
# ─────────────────────────────────────────────────────────────────────────────

async def get_ask_question_uc(
    person_repo: PersonRepository = Depends(get_person_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
    ai_provider: AIProvider = Depends(get_claude_client),
) -> AskQuestionUseCase:
    return AskQuestionUseCase(person_repo, document_repo, ai_provider)


async def get_semantic_search_uc(
    person_repo: PersonRepository = Depends(get_person_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    ai_provider: AIProvider = Depends(get_claude_client),
) -> SemanticSearchUseCase:
    return SemanticSearchUseCase(person_repo, document_repo, chunk_repo, embedding_service, ai_provider)


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    """Получить текущего пользователя из JWT токена."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")

    try:
        payload = JWTHandler.decode_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = await user_repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


def require_role(*allowed_roles: str):
    """Декоратор для проверки роли пользователя."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker
