from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.v1.schemas.auth_schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.domain.errors import InactiveUserError, InvalidCredentialsError, UserAlreadyExistsError
from app.domain.entities import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.use_cases.auth import LoginUserUseCase, RegisterUserUseCase
from app.wiring import build_user_repository, get_session_dependency


router = APIRouter(prefix="/auth", tags=["authentication"])


async def get_user_repo(session: AsyncSession = Depends(get_session_dependency)) -> UserRepository:
	return build_user_repository(session)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
	payload: RegisterRequest,
	user_repo: UserRepository = Depends(get_user_repo),
) -> AuthResponse:
	"""Регистрация нового пользователя."""
	use_case = RegisterUserUseCase(user_repo)
	
	try:
		result = await use_case.execute(
			email=payload.email,
			password=payload.password,
		)
	except UserAlreadyExistsError as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"User with email '{exc.email}' already exists",
		) from exc
	
	return AuthResponse(
		user=UserResponse(
			id=result.user.id,
			email=result.user.email,
			role=result.user.role.value,
			is_active=result.user.is_active,
			created_at=result.user.created_at,
		),
		access_token=result.access_token,
	)


@router.post("/login", response_model=AuthResponse)
async def login(
	payload: LoginRequest,
	user_repo: UserRepository = Depends(get_user_repo),
) -> AuthResponse:
	"""Авторизация пользователя."""
	use_case = LoginUserUseCase(user_repo)
	
	try:
		result = await use_case.execute(
			email=payload.email,
			password=payload.password,
		)
	except InvalidCredentialsError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid email or password",
		) from exc
	except InactiveUserError as exc:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="User account is inactive",
		) from exc
	
	return AuthResponse(
		user=UserResponse(
			id=result.user.id,
			email=result.user.email,
			role=result.user.role.value,
			is_active=result.user.is_active,
			created_at=result.user.created_at,
		),
		access_token=result.access_token,
	)


@router.get("/me", response_model=UserResponse)
async def me(
	current_user: User = Depends(get_current_user),
) -> UserResponse:
	"""Получить данные текущего пользователя по JWT токену."""
	return UserResponse(
		id=current_user.id,
		email=current_user.email,
		role=current_user.role.value,
		is_active=current_user.is_active,
		created_at=current_user.created_at,
	)
