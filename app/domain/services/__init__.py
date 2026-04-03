"""Domain services module."""

from app.domain.services.document_parser import DocumentParser
from app.domain.services.document_storage import DocumentStorage

__all__ = ["DocumentParser", "DocumentStorage"]
