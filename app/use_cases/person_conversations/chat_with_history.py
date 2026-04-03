"""Use case for chat with conversation history."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.entities.person_conversation import PersonConversation, PersonMessage
from app.domain.errors import PersonNotFoundError
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.infrastructure.repositories.person_conversation_repository import PersonConversationRepository
from app.providers import AIProvider, DocumentRepository, PersonRepository


@dataclass
class SourceReference:
    """Reference to a source chunk."""
    document_id: str
    document_name: str
    chunk_text: str
    relevance_score: float

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "chunk_text": self.chunk_text,
            "relevance_score": self.relevance_score,
        }


@dataclass
class ChatWithHistoryResult:
    """Result of chat with history."""
    conversation_id: UUID
    message: PersonMessage
    sources: list[SourceReference]


class ChatWithHistoryUseCase:
    """Use case для чата с учётом истории диалога."""

    CONTEXT_MESSAGE_LIMIT = 6  # Number of recent messages to include in context
    TOP_K_CHUNKS = 3

    def __init__(
        self,
        person_repo: PersonRepository,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        conversation_repo: PersonConversationRepository,
        embedding_service: EmbeddingService,
        ai_provider: AIProvider,
    ) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo
        self._chunk_repo = chunk_repo
        self._conversation_repo = conversation_repo
        self._embedding_service = embedding_service
        self._ai_provider = ai_provider

    async def execute(
        self,
        person_id: UUID,
        question: str,
        conversation_id: UUID | None = None,
        use_semantic_search: bool = True,
        top_k: int | None = None,
    ) -> ChatWithHistoryResult:
        """Execute chat with conversation history.
        
        Args:
            person_id: ID of the person
            question: User's question
            conversation_id: Existing conversation ID (creates new if None)
            use_semantic_search: Whether to use semantic search
            top_k: Number of chunks to retrieve
        
        Returns:
            ChatWithHistoryResult with conversation_id and assistant message
        """
        top_k = top_k or self.TOP_K_CHUNKS

        # 1. Verify person exists
        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        # 2. Get or create conversation
        if conversation_id is None:
            # Create new conversation with title from first question
            title = question[:100] + "..." if len(question) > 100 else question
            conversation = PersonConversation(
                id=uuid4(),
                person_id=person_id,
                title=title,
            )
            conversation = await self._conversation_repo.create(conversation)
            conversation_id = conversation.id
            history_messages = []
        else:
            # Get existing conversation and recent messages
            conversation = await self._conversation_repo.get_by_id(conversation_id)
            if conversation is None or conversation.person_id != person_id:
                raise ValueError("Conversation not found or doesn't belong to this person")
            history_messages = await self._conversation_repo.get_recent_messages(
                conversation_id, limit=self.CONTEXT_MESSAGE_LIMIT
            )

        # 3. Save user message
        user_message = PersonMessage(
            id=uuid4(),
            conversation_id=conversation_id,
            role="user",
            content=question,
        )
        await self._conversation_repo.add_message(user_message)

        # 4. Get documents
        documents = await self._document_repo.get_by_person_id(person_id)
        if not documents:
            # No documents - still respond but note it
            answer = "Для этой карточки нет загруженных документов. Загрузите документы, чтобы задавать вопросы."
            assistant_message = PersonMessage(
                id=uuid4(),
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
            )
            await self._conversation_repo.add_message(assistant_message)
            return ChatWithHistoryResult(
                conversation_id=conversation_id,
                message=assistant_message,
                sources=[],
            )

        doc_lookup = {doc.id: doc for doc in documents}
        sources: list[SourceReference] = []

        # 5. Get relevant context
        if use_semantic_search:
            # Semantic search for relevant chunks
            question_embedding = await self._embedding_service.get_embedding(question)
            search_results = await self._chunk_repo.search_by_person(
                query_embedding=question_embedding,
                person_id=person_id,
                limit=top_k,
            )

            if search_results:
                context_parts = []
                for result in search_results:
                    doc = doc_lookup.get(result.chunk.document_id)
                    doc_name = doc.filename if doc else "Неизвестный документ"
                    context_parts.append(
                        f"[Из документа: {doc_name}]\n{result.chunk.content}"
                    )
                    sources.append(SourceReference(
                        document_id=str(result.chunk.document_id),
                        document_name=doc_name,
                        chunk_text=result.chunk.content[:200] + "..." if len(result.chunk.content) > 200 else result.chunk.content,
                        relevance_score=result.similarity,
                    ))
                documents_context = "\n\n".join(context_parts)
            else:
                # Fallback to full documents
                documents_context = "\n\n".join(
                    f"[Документ: {doc.filename}]\n{doc.content}" for doc in documents
                )
                for doc in documents:
                    sources.append(SourceReference(
                        document_id=str(doc.id),
                        document_name=doc.filename,
                        chunk_text=doc.content[:200] + "...",
                        relevance_score=1.0,
                    ))
        else:
            # Use full documents
            documents_context = "\n\n".join(
                f"[Документ: {doc.filename}]\n{doc.content}" for doc in documents
            )
            for doc in documents:
                sources.append(SourceReference(
                    document_id=str(doc.id),
                    document_name=doc.filename,
                    chunk_text=doc.content[:200] + "...",
                    relevance_score=1.0,
                ))

        # 6. Build context with person info and history
        person_info = f"""Информация о человеке:
- ФИО: {person.full_name}
- Год рождения: {person.birth_year}
- Год смерти: {person.death_year if person.death_year else "неизвестен"}
- Регион: {person.region}
- Обвинение: {person.accusation}
- Биография: {person.biography}
"""

        # Build conversation history context
        history_context = ""
        if history_messages:
            history_parts = []
            for msg in history_messages:
                role_label = "Пользователь" if msg.role == "user" else "Ассистент"
                history_parts.append(f"{role_label}: {msg.content}")
            history_context = "\n\nИстория диалога:\n" + "\n".join(history_parts)

        full_context = f"{person_info}\n\nДокументы:{documents_context}{history_context}"

        # 7. Get answer from LLM
        answer = await self._ai_provider.ask_with_context(full_context, question)

        # 8. Save assistant message with sources
        assistant_message = PersonMessage(
            id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            sources=[s.to_dict() for s in sources],
        )
        await self._conversation_repo.add_message(assistant_message)

        return ChatWithHistoryResult(
            conversation_id=conversation_id,
            message=assistant_message,
            sources=sources,
        )
