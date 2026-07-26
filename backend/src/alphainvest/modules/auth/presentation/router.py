from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.core.config import Settings, get_settings
from alphainvest.infrastructure.database.session import get_db_session
from alphainvest.modules.auth.application.service import AuthService
from alphainvest.modules.auth.domain.exceptions import (
    AccountUnavailable,
    DuplicateEmail,
    InvalidCredentials,
    InvalidRefreshToken,
)
from alphainvest.modules.auth.presentation.dependencies import AuthContext, current_context
from alphainvest.modules.auth.presentation.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    try:
        return await AuthService(session, settings).register(data, client_ip(request))
    except DuplicateEmail as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        ) from err


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    try:
        return await AuthService(session, settings).login(
            str(data.correo), data.password, client_ip(request), request.headers.get("user-agent")
        )
    except InvalidCredentials as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        ) from err
    except AccountUnavailable as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta no disponible",
        ) from err


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    data: RefreshRequest,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    try:
        return await AuthService(session, settings).refresh(data.refresh_token)
    except InvalidRefreshToken as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        ) from err


@router.post("/logout", status_code=204)
async def logout(
    data: LogoutRequest,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> None:
    await AuthService(session, settings).logout(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(ctx: AuthContext = Depends(current_context)) -> UserResponse:
    return ctx.user
