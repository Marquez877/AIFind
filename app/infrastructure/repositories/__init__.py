from .document_repository import SQLAlchemyDocumentRepository
from .person_repository import SQLAlchemyPersonRepository

__all__ = [
    "SQLAlchemyPersonRepository",
    "SQLAlchemyDocumentRepository",
]
