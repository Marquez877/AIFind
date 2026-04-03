from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_conversation_repo,
    get_create_conversation_uc,
    get_send_message_uc,
)
from app.api.v1.schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageResponse,
    MessageSendRequest,
)
from app.domain.errors import ConversationNotFoundError, CustomerNotFoundError
from app.providers import ConversationRepository
from app.use_cases.conversations import CreateConversationUseCase, SendMessageUseCase


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateRequest,
    use_case: CreateConversationUseCase = Depends(get_create_conversation_uc),
) -> ConversationResponse:
    try:
        conversation = await use_case.execute(payload.customer_id, payload.title)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found") from exc

    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    conv_repo: ConversationRepository = Depends(get_conversation_repo),
) -> list[MessageResponse]:
    conversation = await conv_repo.get_by_id(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = await conv_repo.get_messages(conversation_id)

    return [MessageResponse.model_validate(message) for message in messages]


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: UUID,
    payload: MessageSendRequest,
    use_case: SendMessageUseCase = Depends(get_send_message_uc),
) -> MessageResponse:
    try:
        message = await use_case.execute(conversation_id, payload.content)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from exc

    return MessageResponse.model_validate(message)
