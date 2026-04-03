from dataclasses import dataclass
from uuid import UUID

from app.domain.errors import PersonNotFoundError
from app.providers import AIProvider, DocumentRepository, PersonRepository


@dataclass
class ChatResult:
    """Результат RAG-запроса."""
    answer: str
    sources: list[str]


class AskQuestionUseCase:
    """Use case для ответа на вопрос на основе документов (RAG)."""

    def __init__(
        self,
        person_repo: PersonRepository,
        document_repo: DocumentRepository,
        ai_provider: AIProvider,
    ) -> None:
        self._person_repo = person_repo
        self._document_repo = document_repo
        self._ai_provider = ai_provider

    async def execute(self, person_id: UUID, question: str) -> ChatResult:
        # 1. Проверить что карточка существует
        person = await self._person_repo.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(person_id)

        # 2. Получить все документы для карточки
        documents = await self._document_repo.get_by_person_id(person_id)

        if not documents:
            return ChatResult(
                answer="Для этой карточки нет загруженных документов. Загрузите документы, чтобы задавать вопросы.",
                sources=[],
            )

        # 3. Сформировать контекст из документов
        context_parts = []
        sources = []
        for doc in documents:
            context_parts.append(f"--- Документ: {doc.filename} ---\n{doc.content}")
            sources.append(doc.filename)

        context = "\n\n".join(context_parts)

        # 4. Добавить информацию о человеке в контекст
        person_info = f"""--- Информация о человеке ---
ФИО: {person.full_name}
Год рождения: {person.birth_year}
Год смерти: {person.death_year if person.death_year else "неизвестен"}
Регион: {person.region}
Обвинение: {person.accusation}
Биография: {person.biography}
"""
        full_context = person_info + "\n\n" + context

        # 5. Вызвать LLM
        answer = await self._ai_provider.ask_with_context(full_context, question)

        return ChatResult(answer=answer, sources=sources)
