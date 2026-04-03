from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.value_objects import UserRole
from app.infrastructure.db.models import UserModel


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            role=entity.role.value,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )

    async def get_by_id(self, id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def save(self, user: User) -> User:
        """Сохранить (создать или обновить) пользователя."""
        existing_result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = existing_result.scalar_one_or_none()

        if model is None:
            model = self._to_model(user)
            self._session.add(model)
        else:
            model.email = user.email
            model.password_hash = user.password_hash
            model.role = user.role.value
            model.is_active = user.is_active

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        """Удалить пользователя."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return

        await self._session.delete(model)
        await self._session.commit()
