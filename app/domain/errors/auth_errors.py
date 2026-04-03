class UserNotFoundError(Exception):
    """Пользователь не найден."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' not found")


class UserAlreadyExistsError(Exception):
    """Пользователь с таким email уже существует."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(Exception):
    """Неверный email или пароль."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveUserError(Exception):
    """Пользователь деактивирован."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User '{email}' is inactive")


class UnauthorizedError(Exception):
    """Пользователь не авторизован."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message)


class ForbiddenError(Exception):
    """Недостаточно прав для выполнения операции."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message)
