from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.infrastructure.ai.claude_client import ClaudeClient
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.db.session import get_session
from app.infrastructure.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyCustomerRepository,
    SQLAlchemyDocumentRepository,
    SQLAlchemyPersonRepository,
)
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.infrastructure.repositories.person_conversation_repository import PersonConversationRepository
from app.providers import AIProvider, ConversationRepository, CustomerRepository, DocumentRepository, PersonRepository


def build_customer_repository(session: AsyncSession) -> CustomerRepository:
    return SQLAlchemyCustomerRepository(session)


def build_conversation_repository(session: AsyncSession) -> ConversationRepository:
    return SQLAlchemyConversationRepository(session)


def build_person_repository(session: AsyncSession) -> PersonRepository:
    return SQLAlchemyPersonRepository(session)


def build_document_repository(session: AsyncSession) -> DocumentRepository:
    return SQLAlchemyDocumentRepository(session)


def build_chunk_repository(session: AsyncSession) -> ChunkRepository:
    return ChunkRepository(session)


def build_ai_provider() -> AIProvider:
    return ClaudeClient(api_key=settings.ANTHROPIC_API_KEY)


def build_embedding_service() -> EmbeddingService:
    return EmbeddingService(api_key=settings.OPENAI_API_KEY)


def build_person_conversation_repository(session: AsyncSession) -> PersonConversationRepository:
    return PersonConversationRepository(session)


get_session_dependency = get_session
