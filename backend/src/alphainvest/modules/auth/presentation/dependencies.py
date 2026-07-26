from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.core.config import Settings, get_settings
from alphainvest.infrastructure.database.session import get_db_session
from alphainvest.modules.auth.infrastructure.repositories import AuthRepository
from alphainvest.modules.auth.infrastructure.security import TokenService
from alphainvest.modules.auth.presentation.schemas import UserResponse

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user: UserResponse
    session_id: UUID


async def current_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token requerido")
    try:
        payload = TokenService(settings).decode(
            credentials.credentials,
            "access",
        )
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        ) from err
    except jwt.PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from err
    repo = AuthRepository(session)
    user = await repo.get_user(UUID(payload["sub"]))
    stored = await session.get(
        __import__(
            "alphainvest.modules.auth.infrastructure.models", fromlist=["SessionModel"]
        ).SessionModel,
        UUID(payload["sid"]),
    )
    if user is None or user.estado != "ACTIVO" or stored is None or not stored.activa:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión inválida")
    roles, perms = repo.roles_permissions(user)
    return AuthContext(
        UserResponse(
            id=user.id,
            nombres=user.nombres,
            apellidos=user.apellidos,
            correo=user.correo,
            estado=user.estado,
            correo_verificado=user.correo_verificado,
            roles=roles,
            permisos=perms,
        ),
        UUID(payload["sid"]),
    )


def require_permission(
    code: str,
) -> Callable[..., Coroutine[Any, Any, AuthContext]]:
    async def dependency(
        ctx: AuthContext = Depends(current_context),
    ) -> AuthContext:
        if code not in ctx.user.permisos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permiso insuficiente",
            )

        return ctx

    return dependency
