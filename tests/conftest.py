from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.entities import Document, Person, User
from app.domain.value_objects import UserRole


@pytest.fixture
def sample_person() -> Person:
    return Person(
        id=uuid4(),
        full_name="Иван Иванов",
        birth_year=1901,
        death_year=1938,
        region="Алматы",
        accusation="58-10",
        biography="Краткая биография из архивного дела.",
    )


@pytest.fixture
def sample_document(sample_person: Person) -> Document:
    return Document(
        id=uuid4(),
        person_id=sample_person.id,
        filename="archive_note.txt",
        content="Содержимое документа о деле.",
    )


@pytest.fixture
def sample_user() -> User:
    return User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
        role=UserRole.USER,
        is_active=True,
        created_at=datetime.utcnow(),
    )
