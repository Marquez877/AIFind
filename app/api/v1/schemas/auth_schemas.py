from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию."""
    
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль (минимум 8 символов)")


class LoginRequest(BaseModel):
    """Схема запроса на авторизацию."""
    
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Тип токена")


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""
    
    id: UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """Схема ответа при регистрации/авторизации."""
    
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
