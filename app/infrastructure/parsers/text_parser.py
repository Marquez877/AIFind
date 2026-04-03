"""Text file parser implementation."""

from app.domain.services.document_parser import DocumentParser
from app.domain.value_objects.document_type import DocumentType


class TextParser(DocumentParser):
    """Парсер текстовых файлов (.txt, .md)."""

    @property
    def supported_types(self) -> list[DocumentType]:
        return [DocumentType.TXT, DocumentType.MARKDOWN]

    async def parse(self, content: bytes, filename: str) -> str:
        """
        Извлечь текст из текстового файла.

        Поддерживает кодировки: UTF-8, CP1251 (Windows-1251), Latin-1.
        """
        # Пробуем разные кодировки
        encodings = ["utf-8", "cp1251", "latin-1"]
        text = None

        for encoding in encodings:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            raise ValueError(
                f"Cannot decode file '{filename}'. "
                f"Supported encodings: {', '.join(encodings)}"
            )

        # Убираем BOM если есть
        if text.startswith("\ufeff"):
            text = text[1:]

        return text.strip()
