from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import (
    UUID as PostgreSQLUUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from alphainvest.infrastructure.database.base import Base
from alphainvest.modules.auth.infrastructure.models import (
    UserModel,
)
from alphainvest.modules.market.infrastructure.models import (
    AssetModel,
)


class WatchlistModel(Base):
    __tablename__ = "listas_seguimiento"
    __table_args__ = (
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_listas_seguimiento_nombre",
        ),
        CheckConstraint(
            """
            descripcion IS NULL
            OR length(trim(descripcion)) > 0
            """,
            name="ck_listas_seguimiento_descripcion",
        ),
        UniqueConstraint(
            "usuario_id",
            "nombre",
            name=(
                "uq_listas_seguimiento_"
                "usuario_nombre"
            ),
        ),
        Index(
            "idx_listas_seguimiento_usuario",
            "usuario_id",
            "activa",
        ),
        {"schema": "portfolio"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "app_auth.usuarios.id",
            name="fk_listas_seguimiento_usuario",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    predeterminada: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
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

    usuario: Mapped[UserModel] = relationship(
        lazy="joined",
    )

    activos: Mapped[list[WatchlistAssetModel]] = (
        relationship(
            back_populates="lista",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )


class WatchlistAssetModel(Base):
    __tablename__ = "lista_activos"
    __table_args__ = (
        CheckConstraint(
            """
            precio_objetivo IS NULL
            OR precio_objetivo >= 0
            """,
            name="ck_lista_activos_precio_objetivo",
        ),
        CheckConstraint(
            """
            precio_alerta_minimo IS NULL
            OR precio_alerta_minimo >= 0
            """,
            name="ck_lista_activos_alerta_minimo",
        ),
        CheckConstraint(
            """
            precio_alerta_maximo IS NULL
            OR precio_alerta_maximo >= 0
            """,
            name="ck_lista_activos_alerta_maximo",
        ),
        CheckConstraint(
            """
            precio_alerta_minimo IS NULL
            OR precio_alerta_maximo IS NULL
            OR precio_alerta_maximo
                >= precio_alerta_minimo
            """,
            name="ck_lista_activos_rango_alertas",
        ),
        CheckConstraint(
            """
            notas IS NULL
            OR length(trim(notas)) > 0
            """,
            name="ck_lista_activos_notas",
        ),
        Index(
            "idx_lista_activos_activo",
            "activo_id",
        ),
        {"schema": "portfolio"},
    )

    lista_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "portfolio.listas_seguimiento.id",
            name="fk_lista_activos_lista",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            name="fk_lista_activos_activo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )

    precio_objetivo: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(20, 8),
            nullable=True,
        )
    )

    precio_alerta_minimo: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(20, 8),
            nullable=True,
        )
    )

    precio_alerta_maximo: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(20, 8),
            nullable=True,
        )
    )

    notas: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    fecha_agregado: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    lista: Mapped[WatchlistModel] = relationship(
        back_populates="activos",
    )

    activo: Mapped[AssetModel] = relationship(
        lazy="joined",
    )


class PortfolioModel(Base):
    __tablename__ = "portafolios"
    __table_args__ = (
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_portafolios_nombre",
        ),
        CheckConstraint(
            """
            descripcion IS NULL
            OR length(trim(descripcion)) > 0
            """,
            name="ck_portafolios_descripcion",
        ),
        CheckConstraint(
            """
            moneda_base = upper(moneda_base)
            AND moneda_base ~ '^[A-Z]{3}$'
            """,
            name="ck_portafolios_moneda_base",
        ),
        CheckConstraint(
            "capital_inicial >= 0",
            name="ck_portafolios_capital_inicial",
        ),
        CheckConstraint(
            "saldo_efectivo >= 0",
            name="ck_portafolios_saldo_efectivo",
        ),
        CheckConstraint(
            """
            tipo IN (
                'VIRTUAL',
                'SIMULADO'
            )
            """,
            name="ck_portafolios_tipo",
        ),
        CheckConstraint(
            """
            estado IN (
                'ACTIVO',
                'CERRADO',
                'ARCHIVADO'
            )
            """,
            name="ck_portafolios_estado",
        ),
        CheckConstraint(
            """
            fecha_cierre IS NULL
            OR fecha_cierre >= fecha_inicio
            """,
            name="ck_portafolios_fechas",
        ),
        CheckConstraint(
            """
            estado <> 'CERRADO'
            OR fecha_cierre IS NOT NULL
            """,
            name="ck_portafolios_estado_cierre",
        ),
        UniqueConstraint(
            "usuario_id",
            "nombre",
            name="uq_portafolios_usuario_nombre",
        ),
        Index(
            "idx_portafolios_usuario_estado",
            "usuario_id",
            "estado",
        ),
        {"schema": "portfolio"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "app_auth.usuarios.id",
            name="fk_portafolios_usuario",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    moneda_base: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default=text("'USD'"),
    )

    capital_inicial: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    saldo_efectivo: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'VIRTUAL'"),
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'ACTIVO'"),
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
    )

    fecha_cierre: Mapped[date | None] = mapped_column(
        Date,
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

    usuario: Mapped[UserModel] = relationship(
        lazy="joined",
    )

    posiciones: Mapped[list[PositionModel]] = (
        relationship(
            back_populates="portafolio",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )

    valoraciones: Mapped[
        list[PortfolioValuationModel]
    ] = relationship(
        back_populates="portafolio",
        cascade="all, delete-orphan",
        order_by=(
            "PortfolioValuationModel.fecha_hora"
        ),
        lazy="selectin",
    )


class PositionModel(Base):
    __tablename__ = "posiciones"
    __table_args__ = (
        CheckConstraint(
            "cantidad >= 0",
            name="ck_posiciones_cantidad",
        ),
        CheckConstraint(
            "precio_promedio_compra >= 0",
            name="ck_posiciones_precio_promedio",
        ),
        CheckConstraint(
            "costo_total >= 0",
            name="ck_posiciones_costo_total",
        ),
        CheckConstraint(
            """
            precio_actual IS NULL
            OR precio_actual >= 0
            """,
            name="ck_posiciones_precio_actual",
        ),
        CheckConstraint(
            """
            valor_actual IS NULL
            OR valor_actual >= 0
            """,
            name="ck_posiciones_valor_actual",
        ),
        CheckConstraint(
            """
            moneda = upper(moneda)
            AND moneda ~ '^[A-Z]{3}$'
            """,
            name="ck_posiciones_moneda",
        ),
        CheckConstraint(
            """
            estado IN (
                'ABIERTA',
                'CERRADA'
            )
            """,
            name="ck_posiciones_estado",
        ),
        CheckConstraint(
            """
            fecha_cierre IS NULL
            OR fecha_cierre >= fecha_apertura
            """,
            name="ck_posiciones_fecha_cierre",
        ),
        CheckConstraint(
            """
            estado <> 'CERRADA'
            OR fecha_cierre IS NOT NULL
            """,
            name="ck_posiciones_estado_fecha_cierre",
        ),
        CheckConstraint(
            """
            estado <> 'CERRADA'
            OR cantidad = 0
            """,
            name="ck_posiciones_cerrada_cantidad",
        ),
        UniqueConstraint(
            "portafolio_id",
            "activo_id",
            name=(
                "uq_posiciones_"
                "portafolio_activo"
            ),
        ),
        Index(
            "idx_posiciones_portafolio_estado",
            "portafolio_id",
            "estado",
        ),
        Index(
            "idx_posiciones_activo",
            "activo_id",
        ),
        {"schema": "portfolio"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    portafolio_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "portfolio.portafolios.id",
            name="fk_posiciones_portafolio",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            name="fk_posiciones_activo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    precio_promedio_compra: Mapped[
        Decimal
    ] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    costo_total: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    precio_actual: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(20, 8),
            nullable=True,
        )
    )

    valor_actual: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(24, 8),
            nullable=True,
        )
    )

    ganancia_perdida: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    rendimiento_porcentaje: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'ABIERTA'"),
    )

    fecha_apertura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_cierre: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )

    portafolio: Mapped[PortfolioModel] = relationship(
        back_populates="posiciones",
    )

    activo: Mapped[AssetModel] = relationship(
        lazy="joined",
    )


class PortfolioValuationModel(Base):
    __tablename__ = "valoraciones_portafolio"
    __table_args__ = (
        CheckConstraint(
            "saldo_efectivo >= 0",
            name="ck_valoraciones_saldo_efectivo",
        ),
        CheckConstraint(
            "valor_posiciones >= 0",
            name="ck_valoraciones_valor_posiciones",
        ),
        CheckConstraint(
            "valor_total >= 0",
            name="ck_valoraciones_valor_total",
        ),
        CheckConstraint(
            "capital_invertido >= 0",
            name="ck_valoraciones_capital_invertido",
        ),
        CheckConstraint(
            """
            moneda = upper(moneda)
            AND moneda ~ '^[A-Z]{3}$'
            """,
            name="ck_valoraciones_moneda",
        ),
        CheckConstraint(
            """
            abs(
                valor_total
                - (
                    saldo_efectivo
                    + valor_posiciones
                )
            ) <= 0.01
            """,
            name="ck_valoraciones_total_componentes",
        ),
        CheckConstraint(
            """
            detalle IS NULL
            OR jsonb_typeof(detalle) = 'object'
            """,
            name="ck_valoraciones_detalle_json",
        ),
        UniqueConstraint(
            "portafolio_id",
            "fecha_hora",
            name=(
                "uq_valoraciones_"
                "portafolio_fecha"
            ),
        ),
        Index(
            "idx_valoraciones_portafolio_fecha",
            "portafolio_id",
            text("fecha_hora DESC"),
        ),
        {"schema": "portfolio"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    portafolio_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "portfolio.portafolios.id",
            name="fk_valoraciones_portafolio",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    saldo_efectivo: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    valor_posiciones: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    capital_invertido: Mapped[Decimal] = (
        mapped_column(
            Numeric(24, 8),
            nullable=False,
        )
    )

    ganancia_perdida: Mapped[Decimal] = (
        mapped_column(
            Numeric(24, 8),
            nullable=False,
        )
    )

    rendimiento_porcentaje: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    detalle: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    portafolio: Mapped[PortfolioModel] = relationship(
        back_populates="valoraciones",
    )