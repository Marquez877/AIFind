from dataclasses import dataclass
from uuid import uuid4

from app.domain.entities import User
from app.domain.errors import UserAlreadyExistsError
from app.domain.value_objects import UserRole
from app.infrastructure.auth import JWTHandler
from app.infrastructure.repositories.user_repository import UserRepository


@dataclass
class RegisterResult:
    """Результат регистрации пользователя."""
    user: User
    access_token: str


class RegisterUserUseCase:
    """Use case для регистрации нового пользователя."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
    ) -> RegisterResult:
        """Зарегистрировать нового пользователя.
        
        Args:
            email: Email пользователя
            password: Пароль (будет захеширован)
            role: Роль пользователя (по умолчанию USER)
        
        Returns:
            RegisterResult с пользователем и JWT токеном
        
        Raises:
            UserAlreadyExistsError: Если пользователь с таким email уже существует
        """
        # Проверить что пользователь не существует
        existing_user = await self._user_repo.get_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(email)

        # Хешировать пароль
        password_hash = JWTHandler.hash_password(password)

        # Создать пользователя
        user = User(
            id=uuid4(),
            email=email.strip().lower(),
            password_hash=password_hash,
            role=role,
            is_active=True,
        )

        # Сохранить в БД
        saved_user = await self._user_repo.save(user)

        # Создать JWT токен
        access_token = JWTHandler.create_access_token(
            data={"sub": saved_user.email, "role": saved_user.role.value}
        )

        return RegisterResult(user=saved_user, access_token=access_token)
