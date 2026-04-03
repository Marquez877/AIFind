"""Parser factory for selecting appropriate parser by document type."""

from app.domain.services.document_parser import DocumentParser
from app.domain.value_objects.document_type import DocumentType
from app.infrastructure.parsers.pdf_parser import PdfParser
from app.infrastructure.parsers.text_parser import TextParser


class ParserFactory:
    """Фабрика для выбора парсера по типу документа."""

    def __init__(self) -> None:
        self._parsers: list[DocumentParser] = [
            TextParser(),
            PdfParser(),
        ]

    def get_parser(self, doc_type: DocumentType) -> DocumentParser:
        """
        Получить парсер для указанного типа документа.

        Args:
            doc_type: Тип документа

        Returns:
            Подходящий парсер

        Raises:
            ValueError: Если парсер для типа не найден
        """
        for parser in self._parsers:
            if parser.supports(doc_type):
                return parser

        raise ValueError(
            f"No parser found for document type: {doc_type}. "
            f"Supported types: {DocumentType.supported_extensions()}"
        )

    def get_parser_for_file(self, filename: str) -> DocumentParser:
        """
        Получить парсер по имени файла.

        Args:
            filename: Имя файла

        Returns:
            Подходящий парсер
        """
        doc_type = DocumentType.from_filename(filename)
        return self.get_parser(doc_type)

    async def parse_file(self, content: bytes, filename: str) -> str:
        """
        Распарсить файл, автоматически определив тип.

        Args:
            content: Бинарное содержимое файла
            filename: Имя файла

        Returns:
            Извлечённый текст
        """
        parser = self.get_parser_for_file(filename)
        return await parser.parse(content, filename)
