from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.infrastructure.ai.claude_client import ClaudeClient
from app.infrastructure.db.session import get_session
from app.infrastructure.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyCustomerRepository,
    SQLAlchemyDocumentRepository,
    SQLAlchemyPersonRepository,
)
from app.providers import AIProvider, ConversationRepository, CustomerRepository, DocumentRepository, PersonRepository


def build_customer_repository(session: AsyncSession) -> CustomerRepository:
    return SQLAlchemyCustomerRepository(session)


def build_conversation_repository(session: AsyncSession) -> ConversationRepository:
    return SQLAlchemyConversationRepository(session)


def build_person_repository(session: AsyncSession) -> PersonRepository:
    return SQLAlchemyPersonRepository(session)


def build_document_repository(session: AsyncSession) -> DocumentRepository:
    return SQLAlchemyDocumentRepository(session)


def build_ai_provider() -> AIProvider:
    return ClaudeClient(api_key=settings.ANTHROPIC_API_KEY)


get_session_dependency = get_session
