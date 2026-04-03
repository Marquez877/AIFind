from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers import AIProvider, ConversationRepository, CustomerRepository
from app.use_cases.conversations import CreateConversationUseCase, SendMessageUseCase
from app.use_cases.customers import (
	CreateCustomerUseCase,
	DeleteCustomerUseCase,
	GetCustomerUseCase,
	ListCustomersUseCase,
	UpdateCustomerUseCase,
)
from app.wiring import (
	build_ai_provider,
	build_conversation_repository,
	build_customer_repository,
	get_session_dependency,
)


async def get_customer_repo(session: AsyncSession = Depends(get_session_dependency)) -> CustomerRepository:
	return build_customer_repository(session)


async def get_conversation_repo(session: AsyncSession = Depends(get_session_dependency)) -> ConversationRepository:
	return build_conversation_repository(session)


async def get_create_customer_uc(
	repo: CustomerRepository = Depends(get_customer_repo),
) -> CreateCustomerUseCase:
	return CreateCustomerUseCase(repo)


async def get_get_customer_uc(
	repo: CustomerRepository = Depends(get_customer_repo),
) -> GetCustomerUseCase:
	return GetCustomerUseCase(repo)


async def get_list_customers_uc(
	repo: CustomerRepository = Depends(get_customer_repo),
) -> ListCustomersUseCase:
	return ListCustomersUseCase(repo)


async def get_update_customer_uc(
	repo: CustomerRepository = Depends(get_customer_repo),
) -> UpdateCustomerUseCase:
	return UpdateCustomerUseCase(repo)


async def get_delete_customer_uc(
	repo: CustomerRepository = Depends(get_customer_repo),
) -> DeleteCustomerUseCase:
	return DeleteCustomerUseCase(repo)


async def get_create_conversation_uc(
	customer_repo: CustomerRepository = Depends(get_customer_repo),
	conv_repo: ConversationRepository = Depends(get_conversation_repo),
) -> CreateConversationUseCase:
	return CreateConversationUseCase(customer_repo, conv_repo)


async def get_claude_client() -> AIProvider:
	return build_ai_provider()


async def get_send_message_uc(
	conv_repo: ConversationRepository = Depends(get_conversation_repo),
	ai: AIProvider = Depends(get_claude_client),
) -> SendMessageUseCase:
	return SendMessageUseCase(conv_repo, ai)

