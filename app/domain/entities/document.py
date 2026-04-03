from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Document:
    """Документ, прикреплённый к карточке репрессированного."""

    id: UUID
    person_id: UUID  # Связь с карточкой человека
    filename: str  # Имя файла
    content: str  # Содержимое документа
    original_file_path: str | None = None  # Путь к оригинальному файлу (PDF)
    uploaded_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        normalized_filename = self.filename.strip()
        if not normalized_filename:
            raise ValueError("Filename cannot be empty")
        object.__setattr__(self, "filename", normalized_filename)

        if not self.content:
            raise ValueError("Document content cannot be empty")
