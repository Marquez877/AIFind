from uuid import UUID


class DocumentNotFoundError(Exception):
    """Исключение: документ не найден."""

    def __init__(self, document_id: UUID) -> None:
        self.document_id = document_id
        super().__init__(f"Document with id {document_id} not found")
