"""Semantic search use case for RAG with embeddings."""

from dataclasses import dataclass
from typing import AsyncIterator
from uuid import UUID

from app.domain.errors import PersonNotFoundError
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.repositories.chunk_repository import ChunkRepository
from app.providers import AIProvider, DocumentRepository, PersonRepository


@dataclass
class SourceReference:
    """Reference to a source chunk used in the answer."""
    document_id: UUID
    document_name: str
    chunk_text: str
    relevance_score: float


@dataclass
class SemanticChatResult:
    """Result of semantic RAG query with detailed sources."""
    answer: str
    sources: list[SourceReference]


@dataclass
class SemanticSearchPreparedContext:
    """Prepared context and sources for semantic chat."""
    full_context: str | None
    sources: list[SourceReference]
    immediate_answer: str | None = None


class SemanticSearchUseCase:
    """Use case для ответа на вопрос с семантическим поиском по чанкам."""

    TOP_K = 3  # Number of most relevant chunks to retrieve

    def __init__(
        self,
        person_repo: PersonRepository,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        embedding_service: EmbeddingService,
        ai_provider: AIProvider,
    ) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo
        self._chunk_repo = chunk_repo
        self._embedding_service = embedding_service
        self._ai_provider = ai_provider

    async def execute(
        self,
        person_id: UUID,
        question: str,
        top_k: int | None = None,
    ) -> SemanticChatResult:
        """Execute semantic search and generate answer.
        
        Args:
            person_id: ID of the person whose documents to search
            question: User's question
            top_k: Number of chunks to retrieve (default: 3)
        
        Returns:
            SemanticChatResult with answer and source references
        """
        top_k = top_k or self.TOP_K

        prepared = await self.prepare_context(person_id=person_id, question=question, top_k=top_k)
        if prepared.immediate_answer is not None:
            return SemanticChatResult(
                answer=prepared.immediate_answer,
                sources=prepared.sources,
            )

        answer = await self._ai_provider.ask_with_context(prepared.full_context or "", question)
        return SemanticChatResult(answer=answer, sources=prepared.sources)

    async def stream_answer(
        self,
        prepared: SemanticSearchPreparedContext,
        question: str,
    ) -> AsyncIterator[str]:
        if prepared.immediate_answer is not None:
            for token in prepared.immediate_answer:
                yield token
            return

        async for token in self._ai_provider.ask_with_context_stream(prepared.full_context or "", question):
            yield token

    async def prepare_context(
        self,
        person_id: UUID,
        question: str,
        top_k: int | None = None,
    ) -> SemanticSearchPreparedContext:
        top_k = top_k or self.TOP_K

        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        documents = await self._document_repo.get_by_person_id(person_id)
        if not documents:
            return SemanticSearchPreparedContext(
                full_context=None,
                sources=[],
                immediate_answer="Для этой карточки нет загруженных документов. Загрузите документы, чтобы задавать вопросы.",
            )

        doc_lookup = {doc.id: doc for doc in documents}
        question_embedding = await self._embedding_service.get_embedding(question)
        search_results = await self._chunk_repo.search_by_person(
            query_embedding=question_embedding,
            person_id=person_id,
            limit=top_k,
        )

        if not search_results:
            return self._fallback_full_document_context(person, documents)

        context_parts = []
        sources: list[SourceReference] = []
        for result in search_results:
            doc = doc_lookup.get(result.chunk.document_id)
            doc_name = doc.filename if doc else "Неизвестный документ"
            context_parts.append(
                f"--- Фрагмент из {doc_name} (релевантность: {result.similarity:.2f}) ---\n{result.chunk.content}"
            )
            sources.append(SourceReference(
                document_id=result.chunk.document_id,
                document_name=doc_name,
                chunk_text=result.chunk.content[:200] + "..." if len(result.chunk.content) > 200 else result.chunk.content,
                relevance_score=result.similarity,
            ))

        chunks_context = "\n\n".join(context_parts)
        person_info = f"""--- Информация о человеке ---
ФИО: {person.full_name}
Год рождения: {person.birth_year}
Год смерти: {person.death_year if person.death_year else "неизвестен"}
Регион: {person.region}
Обвинение: {person.accusation}
Биография: {person.biography}
"""
        return SemanticSearchPreparedContext(
            full_context=person_info + "\n\n" + chunks_context,
            sources=sources,
        )

    def _fallback_full_document_context(
        self,
        person,
        documents,
    ) -> SemanticSearchPreparedContext:
        """Fallback when no chunks are indexed."""
        context_parts = []
        sources: list[SourceReference] = []

        for doc in documents:
            context_parts.append(f"--- Документ: {doc.filename} ---\n{doc.content}")
            sources.append(SourceReference(
                document_id=doc.id,
                document_name=doc.filename,
                chunk_text=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                relevance_score=1.0,  # Unknown relevance
            ))

        context = "\n\n".join(context_parts)

        person_info = f"""--- Информация о человеке ---
ФИО: {person.full_name}
Год рождения: {person.birth_year}
Год смерти: {person.death_year if person.death_year else "неизвестен"}
Регион: {person.region}
Обвинение: {person.accusation}
Биография: {person.biography}
"""
        full_context = person_info + "\n\n" + context
        return SemanticSearchPreparedContext(full_context=full_context, sources=sources)
