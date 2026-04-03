from dataclasses import dataclass

from app.domain.entities import User
from app.domain.errors import InactiveUserError, InvalidCredentialsError
from app.infrastructure.auth import JWTHandler
from app.infrastructure.repositories.user_repository import UserRepository


@dataclass
class LoginResult:
    """Результат авторизации пользователя."""
    user: User
    access_token: str


class LoginUserUseCase:
    """Use case для авторизации пользователя."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, email: str, password: str) -> LoginResult:
        """Авторизовать пользователя.
        
        Args:
            email: Email пользователя
            password: Пароль
        
        Returns:
            LoginResult с пользователем и JWT токеном
        
        Raises:
            InvalidCredentialsError: Если email или пароль неверный
            InactiveUserError: Если пользователь деактивирован
        """
        # Найти пользователя
        user = await self._user_repo.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        # Проверить пароль
        if not JWTHandler.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        # Проверить что пользователь активен
        if not user.is_active:
            raise InactiveUserError(email)

        # Создать JWT токен
        access_token = JWTHandler.create_access_token(
            data={"sub": user.email, "role": user.role.value}
        )

        return LoginResult(user=user, access_token=access_token)
