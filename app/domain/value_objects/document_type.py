from enum import Enum


class DocumentType(str, Enum):
    """Типы поддерживаемых документов."""

    PDF = "pdf"
    TXT = "txt"
    MARKDOWN = "md"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_filename(cls, filename: str) -> "DocumentType":
        """Определить тип документа по имени файла."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mapping = {
            "pdf": cls.PDF,
            "txt": cls.TXT,
            "md": cls.MARKDOWN,
            "markdown": cls.MARKDOWN,
        }
        if ext not in mapping:
            raise ValueError(f"Unsupported file type: .{ext}")
        return mapping[ext]

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Получить список поддерживаемых расширений."""
        return [".pdf", ".txt", ".md", ".markdown"]
