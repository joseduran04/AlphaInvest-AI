from datetime import UTC, datetime, timedelta
from ipaddress import ip_address
from uuid import UUID, uuid4

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.core.config import Settings
from alphainvest.modules.audit.infrastructure.repository import SecurityAuditRepository
from alphainvest.modules.auth.domain.exceptions import (
    AccountUnavailable,
    DuplicateEmail,
    InvalidCredentials,
    InvalidRefreshToken,
)
from alphainvest.modules.auth.infrastructure.models import (
    SessionModel,
    TermsAcceptanceModel,
    UserModel,
)
from alphainvest.modules.auth.infrastructure.repositories import AuthRepository
from alphainvest.modules.auth.infrastructure.security import PasswordService, TokenService
from alphainvest.modules.auth.presentation.schemas import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.repo = AuthRepository(session)
        self.audit = SecurityAuditRepository(session)
        self.passwords = PasswordService()
        self.tokens = TokenService(settings)

    async def register(self, data: RegisterRequest, ip: str | None) -> UserResponse:
        if await self.repo.get_user_by_email(str(data.correo)):
            raise DuplicateEmail()
        user = UserModel(
            nombres=data.nombres.strip(),
            apellidos=data.apellidos.strip(),
            correo=str(data.correo).lower(),
            password_hash=self.passwords.hash(data.password),
        )
        role = await self.repo.role_by_name(self.settings.default_role)
        if role is None:
            raise RuntimeError(f"No existe el rol base {self.settings.default_role}")
        try:
            await self.repo.add_user(user)
            await self.repo.assign_role(user.id, role.id)
            parsed = None
            if ip:
                try:
                    parsed = ip_address(ip)
                except ValueError:
                    pass
            self.session.add(
                TermsAcceptanceModel(
                    usuario_id=user.id,
                    version_terminos=data.version_terminos,
                    version_privacidad=data.version_privacidad,
                    direccion_ip=parsed,
                )
            )
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateEmail() from exc
        created_user = await self.repo.get_user(user.id)
        if created_user is None:
            raise RuntimeError("El usuario creado no pudo recuperarse")
        return self._user_response(created_user)

    async def login(
        self, email: str, password: str, ip: str | None, user_agent: str | None
    ) -> TokenResponse:
        user = await self.repo.get_user_by_email(email)
        now = datetime.now(UTC)
        if user is None or not self.passwords.verify(password, user.password_hash):
            if user:
                user.intentos_fallidos += 1
                if user.intentos_fallidos >= self.settings.max_failed_login_attempts:
                    user.estado = "BLOQUEADO"
                    user.bloqueado_hasta = now + timedelta(minutes=self.settings.login_lock_minutes)
            await self.audit.record(
                event_type="LOGIN_FALLIDO",
                result="FALLIDO",
                description="Credenciales inválidas",
                user_id=user.id if user else None,
                email=email,
                ip=ip,
                user_agent=user_agent,
                severity="MEDIA",
                metadata={},
            )
            await self.session.commit()
            raise InvalidCredentials()
        if user.estado == "BLOQUEADO" and user.bloqueado_hasta and user.bloqueado_hasta <= now:
            user.estado = "ACTIVO"
            user.bloqueado_hasta = None
        if user.estado != "ACTIVO":
            raise AccountUnavailable()
        session_id = uuid4()
        refresh, expires = self.tokens.create_refresh(user.id, session_id)
        parsed = None
        if ip:
            try:
                parsed = ip_address(ip)
            except ValueError:
                pass
        await self.repo.add_session(
            SessionModel(
                id=session_id,
                usuario_id=user.id,
                refresh_token_hash=self.tokens.hash_refresh(refresh),
                direccion_ip=parsed,
                agente_usuario=user_agent,
                fecha_expiracion=expires,
            )
        )
        user.intentos_fallidos = 0
        user.ultimo_acceso = now
        roles, perms = self.repo.roles_permissions(user)
        access = self.tokens.create_access(user.id, session_id, roles, perms)
        await self.audit.record(
            event_type="LOGIN_EXITOSO",
            result="EXITOSO",
            description="Inicio de sesión exitoso",
            user_id=user.id,
            email=email,
            ip=ip,
            user_agent=user_agent,
            resource="/auth/login",
            metadata={},
        )
        await self.session.commit()
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.access_token_minutes * 60,
        )

    async def refresh(self, token: str) -> TokenResponse:
        try:
            payload = self.tokens.decode(token, "refresh")
        except jwt.PyJWTError as exc:
            raise InvalidRefreshToken() from exc
        stored = await self.repo.session_by_hash(self.tokens.hash_refresh(token))
        now = datetime.now(UTC)
        if stored is None or not stored.activa or stored.fecha_expiracion <= now:
            raise InvalidRefreshToken()
        user = await self.repo.get_user(UUID(payload["sub"]))
        if user is None or user.estado != "ACTIVO":
            raise InvalidRefreshToken()
        await self.repo.revoke_session(stored)
        new_id = uuid4()
        new_refresh, expires = self.tokens.create_refresh(user.id, new_id)
        await self.repo.add_session(
            SessionModel(
                id=new_id,
                usuario_id=user.id,
                refresh_token_hash=self.tokens.hash_refresh(new_refresh),
                direccion_ip=stored.direccion_ip,
                agente_usuario=stored.agente_usuario,
                fecha_expiracion=expires,
            )
        )
        roles, perms = self.repo.roles_permissions(user)
        access = self.tokens.create_access(user.id, new_id, roles, perms)
        await self.session.commit()
        return TokenResponse(
            access_token=access,
            refresh_token=new_refresh,
            expires_in=self.settings.access_token_minutes * 60,
        )

    async def logout(self, token: str) -> None:
        stored = await self.repo.session_by_hash(self.tokens.hash_refresh(token))
        if stored and stored.activa:
            await self.repo.revoke_session(stored)
            await self.audit.record(
                event_type="SESION_REVOCADA",
                result="EXITOSO",
                description="Sesión cerrada",
                user_id=stored.usuario_id,
                resource="/auth/logout",
                metadata={},
            )
            await self.session.commit()

    @staticmethod
    def _user_response(user: UserModel) -> UserResponse:
        roles, perms = AuthRepository.roles_permissions(user)
        return UserResponse(
            id=user.id,
            nombres=user.nombres,
            apellidos=user.apellidos,
            correo=user.correo,
            estado=user.estado,
            correo_verificado=user.correo_verificado,
            roles=roles,
            permisos=perms,
        )
