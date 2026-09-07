from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import CITEXT, INET
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphainvest.infrastructure.database.base import Base


class UserRoleModel(Base):
    __tablename__ = "usuario_roles"
    __table_args__ = {"schema": "app_auth"}

    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_auth.usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rol_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_auth.roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    asignado_por: Mapped[UUID | None] = mapped_column(
        ForeignKey("app_auth.usuarios.id"),
        nullable=True,
    )
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class UserModel(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "app_auth"}

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(CITEXT, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    estado: Mapped[str] = mapped_column(
        String(30),
        server_default="PENDIENTE_VERIFICACION",
    )
    correo_verificado: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
    )
    intentos_fallidos: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
    )
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    roles: Mapped[list["RoleModel"]] = relationship(
        secondary=UserRoleModel.__table__,
        primaryjoin=id == UserRoleModel.usuario_id,
        secondaryjoin=lambda: RoleModel.id == UserRoleModel.rol_id,
        foreign_keys=[
            UserRoleModel.usuario_id,
            UserRoleModel.rol_id,
        ],
        back_populates="usuarios",
        lazy="selectin",
    )


class RoleModel(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "app_auth"}

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    nombre: Mapped[str] = mapped_column(String(50), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    permisos: Mapped[list["PermissionModel"]] = relationship(
        secondary="app_auth.rol_permisos",
        lazy="selectin",
        viewonly=True,
    )

    usuarios: Mapped[list["UserModel"]] = relationship(
        secondary=UserRoleModel.__table__,
        primaryjoin=id == UserRoleModel.rol_id,
        secondaryjoin=lambda: UserModel.id == UserRoleModel.usuario_id,
        foreign_keys=[
            UserRoleModel.usuario_id,
            UserRoleModel.rol_id,
        ],
        back_populates="roles",
        lazy="selectin",
    )


class PermissionModel(Base):
    __tablename__ = "permisos"
    __table_args__ = {"schema": "app_auth"}
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    codigo: Mapped[str] = mapped_column(String(100), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(255))
    modulo: Mapped[str] = mapped_column(String(50))
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RolePermissionModel(Base):
    __tablename__ = "rol_permisos"
    __table_args__ = {"schema": "app_auth"}
    rol_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_auth.roles.id", ondelete="CASCADE"), primary_key=True
    )
    permiso_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_auth.permisos.id", ondelete="CASCADE"), primary_key=True
    )
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SessionModel(Base):
    __tablename__ = "sesiones"
    __table_args__ = {"schema": "app_auth"}
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("app_auth.usuarios.id", ondelete="CASCADE"))
    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    direccion_ip: Mapped[IPv4Address | IPv6Address | None] = mapped_column(INET)
    agente_usuario: Mapped[str | None] = mapped_column(String(500))
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_expiracion: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_revocacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activa: Mapped[bool] = mapped_column(Boolean, server_default="true")


class TermsAcceptanceModel(Base):
    __tablename__ = "aceptaciones_terminos"
    __table_args__ = {"schema": "app_auth"}
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_auth.usuarios.id",
            ondelete="RESTRICT",
        )
    )
    version_terminos: Mapped[str] = mapped_column(String(30))
    version_privacidad: Mapped[str] = mapped_column(String(30))
    fecha_aceptacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    direccion_ip: Mapped[IPv4Address | IPv6Address | None] = mapped_column(INET)
