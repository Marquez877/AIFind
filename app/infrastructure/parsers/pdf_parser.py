"""PDF parser implementation using pdfplumber."""

import io
from typing import TYPE_CHECKING

from app.domain.services.document_parser import DocumentParser
from app.domain.value_objects.document_type import DocumentType

if TYPE_CHECKING:
    pass


class PdfParser(DocumentParser):
    """Парсер PDF-файлов с использованием pdfplumber."""

    @property
    def supported_types(self) -> list[DocumentType]:
        return [DocumentType.PDF]

    async def parse(self, content: bytes, filename: str) -> str:
        """
        Извлечь текст из PDF-документа.

        Сохраняет структуру: абзацы разделяются двойным переносом,
        страницы — тройным.
        """
        try:
            import pdfplumber
        except ImportError as e:
            raise ImportError(
                "pdfplumber is required for PDF parsing. "
                "Install it with: pip install pdfplumber"
            ) from e

        try:
            pages_text: list[str] = []

            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        # Нормализуем пробелы в тексте страницы
                        page_text = self._normalize_text(page_text)
                        pages_text.append(page_text)

            if not pages_text:
                raise ValueError(
                    f"No text could be extracted from PDF '{filename}'. "
                    "The file may be empty, scanned (image-based), or corrupted."
                )

            # Соединяем страницы с разделителем
            full_text = "\n\n---\n\n".join(pages_text)
            return full_text

        except Exception as e:
            if "password" in str(e).lower():
                raise ValueError(
                    f"PDF '{filename}' is password-protected. "
                    "Please provide an unprotected file."
                ) from e
            if isinstance(e, ValueError):
                raise
            raise ValueError(
                f"Failed to parse PDF '{filename}': {e}"
            ) from e

    def _normalize_text(self, text: str) -> str:
        """Нормализовать текст страницы."""
        # Убираем множественные пробелы, но сохраняем переносы строк
        lines = text.split("\n")
        normalized_lines = []

        for line in lines:
            # Убираем множественные пробелы внутри строки
            line = " ".join(line.split())
            if line:  # Пропускаем пустые строки
                normalized_lines.append(line)

        # Соединяем строки с одним переносом
        return "\n".join(normalized_lines)
