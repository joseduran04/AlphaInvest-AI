from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.auth.infrastructure.models import (
    RoleModel,
    SessionModel,
    UserModel,
    UserRoleModel,
)


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> UserModel | None:
        q = (
            select(UserModel)
            .where(UserModel.correo == email)
            .options(selectinload(UserModel.roles).selectinload(RoleModel.permisos))
        )
        return (await self.session.execute(q)).scalar_one_or_none()

    async def get_user(self, user_id: UUID) -> UserModel | None:
        q = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.roles).selectinload(RoleModel.permisos))
        )
        return (await self.session.execute(q)).scalar_one_or_none()

    async def role_by_name(self, name: str) -> RoleModel | None:
        return (
            await self.session.execute(
                select(RoleModel).where(RoleModel.nombre == name, RoleModel.activo.is_(True))
            )
        ).scalar_one_or_none()

    async def add_user(self, user: UserModel) -> None:
        self.session.add(user)
        await self.session.flush()

    async def assign_role(self, user_id: UUID, role_id: UUID) -> None:
        self.session.add(UserRoleModel(usuario_id=user_id, rol_id=role_id))

    async def add_session(self, s: SessionModel) -> None:
        self.session.add(s)
        await self.session.flush()

    async def session_by_hash(self, h: str) -> SessionModel | None:
        return (
            await self.session.execute(
                select(SessionModel).where(SessionModel.refresh_token_hash == h)
            )
        ).scalar_one_or_none()

    async def revoke_session(self, s: SessionModel) -> None:
        s.activa = False
        s.fecha_revocacion = datetime.now(UTC)
        await self.session.flush()

    async def revoke_all(self, user_id: UUID) -> None:
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.usuario_id == user_id, SessionModel.activa.is_(True))
            .values(activa=False, fecha_revocacion=datetime.now(UTC))
        )

    @staticmethod
    def roles_permissions(user: UserModel) -> tuple[list[str], list[str]]:
        roles = sorted({r.nombre for r in user.roles if r.activo})
        perms = sorted({p.codigo for r in user.roles if r.activo for p in r.permisos if p.activo})
        return roles, perms
