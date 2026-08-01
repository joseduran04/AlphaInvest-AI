from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphainvest.infrastructure.database.base import Base


class MarketModel(Base):
    __tablename__ = "mercados"
    __table_args__ = (
        CheckConstraint(
            "length(trim(codigo)) > 0",
            name="ck_mercados_codigo_no_vacio",
        ),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_mercados_nombre_no_vacio",
        ),
        CheckConstraint(
            "length(trim(pais)) > 0",
            name="ck_mercados_pais_no_vacio",
        ),
        CheckConstraint(
            "length(trim(zona_horaria)) > 0",
            name="ck_mercados_zona_horaria_no_vacia",
        ),
        CheckConstraint(
            """
            moneda = upper(moneda)
            AND moneda ~ '^[A-Z]{3}$'
            """,
            name="ck_mercados_moneda",
        ),
        UniqueConstraint(
            "codigo",
            name="uq_mercados_codigo",
        ),
        {"schema": "market"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    codigo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    pais: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    zona_horaria: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
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

    activos: Mapped[list[AssetModel]] = relationship(
        back_populates="mercado",
        lazy="selectin",
    )


class AssetTypeModel(Base):
    __tablename__ = "tipos_activo"
    __table_args__ = (
        CheckConstraint(
            "length(trim(codigo)) > 0",
            name="ck_tipos_activo_codigo_no_vacio",
        ),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_tipos_activo_nombre_no_vacio",
        ),
        UniqueConstraint(
            "codigo",
            name="uq_tipos_activo_codigo",
        ),
        UniqueConstraint(
            "nombre",
            name="uq_tipos_activo_nombre",
        ),
        {"schema": "market"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    codigo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    activos: Mapped[list[AssetModel]] = relationship(
        back_populates="tipo_activo",
        lazy="selectin",
    )


class AssetModel(Base):
    __tablename__ = "activos"
    __table_args__ = (
        CheckConstraint(
            "length(trim(simbolo)) > 0",
            name="ck_activos_simbolo_no_vacio",
        ),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_activos_nombre_no_vacio",
        ),
        CheckConstraint(
            """
            moneda = upper(moneda)
            AND moneda ~ '^[A-Z]{3}$'
            """,
            name="ck_activos_moneda",
        ),
        CheckConstraint(
            """
            isin IS NULL
            OR length(trim(isin)) > 0
            """,
            name="ck_activos_isin_no_vacio",
        ),
        CheckConstraint(
            """
            estado IN (
                'ACTIVO',
                'INACTIVO',
                'SUSPENDIDO'
            )
            """,
            name="ck_activos_estado",
        ),
        UniqueConstraint(
            "mercado_id",
            "simbolo",
            name="uq_activos_mercado_simbolo",
        ),
        UniqueConstraint(
            "isin",
            name="uq_activos_isin",
        ),
        Index(
            "idx_activos_simbolo",
            "simbolo",
        ),
        Index(
            "idx_activos_mercado",
            "mercado_id",
        ),
        Index(
            "idx_activos_tipo",
            "tipo_activo_id",
        ),
        Index(
            "idx_activos_sector",
            "sector",
        ),
        {"schema": "market"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    mercado_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.mercados.id",
            name="fk_activos_mercado",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    tipo_activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.tipos_activo.id",
            name="fk_activos_tipo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    simbolo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    industria: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    isin: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'ACTIVO'"),
    )

    fecha_alta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    mercado: Mapped[MarketModel] = relationship(
        back_populates="activos",
    )

    tipo_activo: Mapped[AssetTypeModel] = relationship(
        back_populates="activos",
    )

    precios_historicos: Mapped[list[HistoricalPriceModel]] = relationship(
    back_populates="activo",
    lazy="selectin",
    )

class FinancialSourceModel(Base):
    __tablename__ = "fuentes_financieras"
    __table_args__ = (
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_fuentes_nombre_no_vacio",
        ),
        CheckConstraint(
            "length(trim(proveedor)) > 0",
            name="ck_fuentes_proveedor_no_vacio",
        ),
        CheckConstraint(
            "prioridad > 0",
            name="ck_fuentes_prioridad",
        ),
        CheckConstraint(
            """
            limite_consultas_minuto IS NULL
            OR limite_consultas_minuto > 0
            """,
            name="ck_fuentes_limite_consultas",
        ),
        CheckConstraint(
            """
            url_base IS NULL
            OR length(trim(url_base)) > 0
            """,
            name="ck_fuentes_url",
        ),
        UniqueConstraint(
            "nombre",
            name="uq_fuentes_financieras_nombre",
        ),
        {"schema": "market"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    proveedor: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    url_base: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    prioridad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    requiere_api_key: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    limite_consultas_minuto: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ultima_consulta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    precios_historicos: Mapped[list[HistoricalPriceModel]] = relationship(
    back_populates="fuente",
    lazy="selectin",
)


class HistoricalPriceModel(Base):
    __tablename__ = "precios_historicos"
    __table_args__ = (
        CheckConstraint(
            "apertura IS NULL OR apertura >= 0",
            name="ck_precios_apertura",
        ),
        CheckConstraint(
            "maximo IS NULL OR maximo >= 0",
            name="ck_precios_maximo",
        ),
        CheckConstraint(
            "minimo IS NULL OR minimo >= 0",
            name="ck_precios_minimo",
        ),
        CheckConstraint(
            "cierre >= 0",
            name="ck_precios_cierre",
        ),
        CheckConstraint(
            """
            cierre_ajustado IS NULL
            OR cierre_ajustado >= 0
            """,
            name="ck_precios_cierre_ajustado",
        ),
        CheckConstraint(
            "volumen IS NULL OR volumen >= 0",
            name="ck_precios_volumen",
        ),
        CheckConstraint(
            """
            maximo IS NULL
            OR minimo IS NULL
            OR maximo >= minimo
            """,
            name="ck_precios_maximo_minimo",
        ),
        CheckConstraint(
            """
            apertura IS NULL
            OR maximo IS NULL
            OR minimo IS NULL
            OR apertura BETWEEN minimo AND maximo
            """,
            name="ck_precios_apertura_rango",
        ),
        CheckConstraint(
            """
            maximo IS NULL
            OR minimo IS NULL
            OR cierre BETWEEN minimo AND maximo
            """,
            name="ck_precios_cierre_rango",
        ),
        CheckConstraint(
            """
            moneda = upper(moneda)
            AND moneda ~ '^[A-Z]{3}$'
            """,
            name="ck_precios_moneda",
        ),
        UniqueConstraint(
            "activo_id",
            "fuente_id",
            "fecha",
            name="uq_precios_activo_fuente_fecha",
        ),
        Index(
            "idx_precios_activo_fecha",
            "activo_id",
            text("fecha DESC"),
        ),
        Index(
            "idx_precios_fuente",
            "fuente_id",
        ),
        {"schema": "market"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            name="fk_precios_historicos_activo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    fuente_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.fuentes_financieras.id",
            name="fk_precios_historicos_fuente",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    apertura: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    maximo: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    minimo: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    cierre: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    cierre_ajustado: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    volumen: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 4),
        nullable=True,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    activo: Mapped[AssetModel] = relationship(
        back_populates="precios_historicos",
    )

    fuente: Mapped[FinancialSourceModel] = relationship(
        back_populates="precios_historicos",
    )