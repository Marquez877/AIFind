"""Domain service interface for storing original document files."""

from abc import ABC, abstractmethod


class DocumentStorage(ABC):
    """Абстракция хранилища оригинальных файлов документов."""

    @abstractmethod
    async def save_original(self, filename: str, content: bytes) -> str:
        """Сохранить оригинальный файл и вернуть путь/ссылку."""
        ...

    @abstractmethod
    async def delete_original(self, stored_path: str) -> None:
        """Удалить оригинальный файл по пути/ссылке."""
        ...
