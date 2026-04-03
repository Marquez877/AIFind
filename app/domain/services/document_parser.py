"""Domain service interfaces for document parsing."""

from abc import ABC, abstractmethod

from app.domain.value_objects.document_type import DocumentType


class DocumentParser(ABC):
    """Абстрактный интерфейс парсера документов (Domain Service)."""

    @property
    @abstractmethod
    def supported_types(self) -> list[DocumentType]:
        """Типы документов, поддерживаемые парсером."""
        ...

    @abstractmethod
    async def parse(self, content: bytes, filename: str) -> str:
        """
        Извлечь текстовое содержимое из документа.

        Args:
            content: Бинарное содержимое файла
            filename: Имя файла (для определения кодировки и т.д.)

        Returns:
            Извлечённый текст

        Raises:
            ValueError: Если файл не может быть распознан
        """
        ...

    def supports(self, doc_type: DocumentType) -> bool:
        """Проверить, поддерживает ли парсер данный тип."""
        return doc_type in self.supported_types
