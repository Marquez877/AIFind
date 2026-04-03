from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTHandler:
    """Обработчик JWT токенов и паролей."""

    SECRET_KEY: str = settings.JWT_SECRET_KEY if hasattr(settings, 'JWT_SECRET_KEY') else "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней

    @staticmethod
    def hash_password(password: str) -> str:
        """Хешировать пароль."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль."""
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """Создать JWT токен."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> dict[str, Any]:
        """Декодировать JWT токен.
        
        Raises:
            JWTError: Если токен невалиден
        """
        return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
