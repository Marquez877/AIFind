"""Local filesystem storage for original document files."""

from pathlib import Path
from uuid import uuid4

from app.domain.services.document_storage import DocumentStorage


class LocalDocumentStorage(DocumentStorage):
    """Локальное файловое хранилище оригиналов документов."""

    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)

    async def save_original(self, filename: str, content: bytes) -> str:
        self._base_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix.lower()
        stored_name = f"{uuid4()}{ext}"
        target_path = self._base_dir / stored_name
        target_path.write_bytes(content)
        return str(target_path)

    async def delete_original(self, stored_path: str) -> None:
        path = Path(stored_path)
        if path.exists():
            path.unlink()
