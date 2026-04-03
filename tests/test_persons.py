from uuid import uuid4

import pytest

from app.domain.entities import Person
from app.domain.errors import PersonAlreadyExistsError
from app.use_cases.persons.create_person import CreatePersonUseCase


class _PersonRepoStub:
    def __init__(self, duplicate: Person | None = None):
        self.duplicate = duplicate
        self.saved_person: Person | None = None
        self.embedding_saved_for: tuple | None = None

    async def find_duplicate(self, full_name: str, birth_year: int) -> Person | None:
        return self.duplicate

    async def save(self, person: Person) -> Person:
        self.saved_person = person
        return person

    async def set_biography_embedding(self, person_id, embedding: list[float]) -> None:
        self.embedding_saved_for = (person_id, embedding)


class _EmbeddingStub:
    async def get_embedding(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_create_person_saves_person_and_embedding():
    repo = _PersonRepoStub()
    use_case = CreatePersonUseCase(repo=repo, embedding_service=_EmbeddingStub())

    person = await use_case.execute(
        full_name="  Иван Петров  ",
        birth_year=1902,
        death_year=1940,
        region="  Алма-Ата ",
        accusation=" 58-10 ",
        biography="  Архивная биография. ",
    )

    assert repo.saved_person is not None
    assert person.full_name == "Иван Петров"
    assert person.region == "Алма-Ата"
    assert person.accusation == "58-10"
    assert person.biography == "Архивная биография."
    assert repo.embedding_saved_for is not None
    assert repo.embedding_saved_for[0] == person.id
    assert repo.embedding_saved_for[1] == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_create_person_raises_when_duplicate_exists(sample_person: Person):
    repo = _PersonRepoStub(duplicate=sample_person)
    use_case = CreatePersonUseCase(repo=repo, embedding_service=_EmbeddingStub())

    with pytest.raises(PersonAlreadyExistsError):
        await use_case.execute(
            full_name=sample_person.full_name,
            birth_year=sample_person.birth_year,
            death_year=sample_person.death_year,
            region=sample_person.region,
            accusation=sample_person.accusation,
            biography=sample_person.biography,
        )
