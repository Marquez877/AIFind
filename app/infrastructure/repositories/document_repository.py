from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Document
from app.infrastructure.db.models import DocumentModel
from app.providers import DocumentRepository


class SQLAlchemyDocumentRepository(DocumentRepository):
    """SQLAlchemy реализация репозитория для документов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            person_id=model.person_id,
            filename=model.filename,
            content=model.content,
            uploaded_at=model.uploaded_at,
        )

    @staticmethod
    def _to_model(entity: Document) -> DocumentModel:
        return DocumentModel(
            id=entity.id,
            person_id=entity.person_id,
            filename=entity.filename,
            content=entity.content,
            uploaded_at=entity.uploaded_at,
        )

    async def get_by_id(self, id: UUID) -> Document | None:
        result = await self._session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_person_id(self, person_id: UUID) -> list[Document]:
        result = await self._session.execute(
            select(DocumentModel)
            .where(DocumentModel.person_id == person_id)
            .order_by(DocumentModel.uploaded_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def save(self, document: Document) -> Document:
        existing_result = await self._session.execute(
            select(DocumentModel).where(DocumentModel.id == document.id)
        )
        model = existing_result.scalar_one_or_none()

        if model is None:
            model = self._to_model(document)
            self._session.add(model)
        else:
            model.filename = document.filename
            model.content = document.content

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        result = await self._session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return

        await self._session.delete(model)
        await self._session.commit()
