from uuid import uuid4

import pytest

from app.domain.entities import Document, Person
from app.providers.person_repository import DuplicateMatch
from app.use_cases.persons.check_duplicates import CheckPersonDuplicatesUseCase
from app.use_cases.rag.semantic_search import SemanticSearchUseCase


class _DupRepoStub:
    def __init__(self, matches):
        self.matches = matches
        self.called_with = None

    async def find_potential_duplicates(self, full_name, birth_year, biography_embedding, limit=5):
        self.called_with = (full_name, birth_year, biography_embedding, limit)
        return self.matches


class _PersonRepoForSemantic:
    def __init__(self, person: Person | None):
        self.person = person

    async def get_by_id(self, person_id):
        return self.person


class _DocumentRepoForSemantic:
    def __init__(self, docs):
        self.docs = docs

    async def get_by_person_id(self, person_id):
        return self.docs


class _ChunkRepoForSemantic:
    def __init__(self, results):
        self.results = results

    async def search_by_person(self, query_embedding, person_id, limit):
        return self.results


class _EmbeddingStub:
    async def get_embedding(self, text):
        return [0.42, 0.11]


class _AIStub:
    async def ask_with_context(self, context, question):
        return "ok"

    async def ask_with_context_stream(self, context, question):
        for token in "ok":
            yield token


@pytest.mark.asyncio
async def test_check_duplicates_passes_embedding_and_limit(sample_person: Person):
    matches = [
        DuplicateMatch(person=sample_person, score=0.9, name_similarity=0.95, biography_similarity=0.85)
    ]
    repo = _DupRepoStub(matches=matches)
    use_case = CheckPersonDuplicatesUseCase(person_repo=repo, embedding_service=_EmbeddingStub())

    result = await use_case.execute(
        full_name="Иван Иванов",
        birth_year=1901,
        biography="Текст биографии",
        limit=3,
    )

    assert result.matches == matches
    assert repo.called_with == ("Иван Иванов", 1901, [0.42, 0.11], 3)


@pytest.mark.asyncio
async def test_semantic_prepare_context_returns_immediate_answer_without_documents(sample_person: Person):
    use_case = SemanticSearchUseCase(
        person_repo=_PersonRepoForSemantic(sample_person),
        document_repo=_DocumentRepoForSemantic([]),
        chunk_repo=_ChunkRepoForSemantic([]),
        embedding_service=_EmbeddingStub(),
        ai_provider=_AIStub(),
    )

    prepared = await use_case.prepare_context(person_id=sample_person.id, question="Кто это?")

    assert prepared.full_context is None
    assert prepared.sources == []
    assert prepared.immediate_answer is not None


@pytest.mark.asyncio
async def test_semantic_prepare_context_fallback_uses_full_documents(sample_person: Person):
    doc = Document(
        id=uuid4(),
        person_id=sample_person.id,
        filename="doc1.txt",
        content="Содержимое архивного документа",
    )
    use_case = SemanticSearchUseCase(
        person_repo=_PersonRepoForSemantic(sample_person),
        document_repo=_DocumentRepoForSemantic([doc]),
        chunk_repo=_ChunkRepoForSemantic([]),
        embedding_service=_EmbeddingStub(),
        ai_provider=_AIStub(),
    )

    prepared = await use_case.prepare_context(person_id=sample_person.id, question="Что известно?")

    assert prepared.full_context is not None
    assert "Информация о человеке" in prepared.full_context
    assert "doc1.txt" in prepared.full_context
    assert len(prepared.sources) == 1
