from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphainvest.infrastructure.database.base import Base


class NotificationModel(Base):
    __tablename__ = "notificaciones"
    __table_args__ = {"schema": "operation"}

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "app_auth.usuarios.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    canal: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    mensaje: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    prioridad: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'NORMAL'"),
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'PENDIENTE'"),
    )

    datos: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_programada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_envio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_lectura: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    intentos_envio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    ultimo_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    referencia_tipo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    referencia_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )


class ScheduledJobModel(Base):
    __tablename__ = "trabajos_programados"
    __table_args__ = {"schema": "operation"}

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    codigo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    expresion_cron: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    intervalo_segundos: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    zona_horaria: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        server_default=text("'UTC'"),
    )

    parametros: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    permite_concurrencia: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    tiempo_maximo_segundos: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    maximo_reintentos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    siguiente_ejecucion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ultima_ejecucion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    creado_por: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    ejecuciones: Mapped[list[JobExecutionModel]] = relationship(
        back_populates="trabajo",
        lazy="selectin",
    )


class JobExecutionModel(Base):
    __tablename__ = "ejecuciones_trabajo"
    __table_args__ = {"schema": "operation"}

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    trabajo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "operation.trabajos_programados.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'PENDIENTE'"),
    )

    numero_intento: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    disparador: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    solicitado_por: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )

    identificador_proceso: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        unique=True,
    )

    fecha_programada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    progreso: Mapped[Decimal] = mapped_column(
        Numeric(7, 4),
        nullable=False,
        server_default=text("0"),
    )

    registros_procesados: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text("0"),
    )

    registros_exitosos: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text("0"),
    )

    registros_fallidos: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text("0"),
    )

    resultado: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    mensaje_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    trabajo: Mapped[ScheduledJobModel] = relationship(
        back_populates="ejecuciones",
    )