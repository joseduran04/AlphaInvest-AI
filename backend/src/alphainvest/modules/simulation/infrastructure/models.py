from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
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
from alphainvest.modules.ai.infrastructure.models import (
    ModelVersionModel,
)
from alphainvest.modules.auth.infrastructure.models import (
    UserModel,
)
from alphainvest.modules.market.infrastructure.models import (
    AssetModel,
)
from alphainvest.modules.portfolio.infrastructure.models import (
    PortfolioModel,
)


class SimulationConfigurationModel(Base):
    __tablename__ = "configuraciones"
    __table_args__ = (
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_configuraciones_nombre",
        ),
        CheckConstraint(
            """
            descripcion IS NULL
            OR length(trim(descripcion)) > 0
            """,
            name="ck_configuraciones_descripcion",
        ),
        CheckConstraint(
            """
            tipo_simulacion IN (
                'HISTORICA',
                'MONTE_CARLO',
                'PROYECCION',
                'ESCENARIO'
            )
            """,
            name="ck_configuraciones_tipo",
        ),
        CheckConstraint(
            "capital_inicial > 0",
            name="ck_configuraciones_capital_inicial",
        ),
        CheckConstraint(
            """
            moneda_base = upper(moneda_base)
            AND moneda_base ~ '^[A-Z]{3}$'
            """,
            name="ck_configuraciones_moneda",
        ),
        CheckConstraint(
            "fecha_fin > fecha_inicio",
            name="ck_configuraciones_fechas",
        ),
        CheckConstraint(
            "aportacion_periodica >= 0",
            name="ck_configuraciones_aportacion",
        ),
        CheckConstraint(
            """
            (
                aportacion_periodica = 0
                AND frecuencia_aportacion IS NULL
            )
            OR
            (
                aportacion_periodica > 0
                AND frecuencia_aportacion IN (
                    'SEMANAL',
                    'QUINCENAL',
                    'MENSUAL',
                    'TRIMESTRAL',
                    'SEMESTRAL',
                    'ANUAL'
                )
            )
            """,
            name="ck_configuraciones_frecuencia_aportacion",
        ),
        CheckConstraint(
            "comision_porcentaje BETWEEN 0 AND 100",
            name="ck_configuraciones_comision",
        ),
        CheckConstraint(
            """
            inflacion_anual IS NULL
            OR inflacion_anual > -100
            """,
            name="ck_configuraciones_inflacion",
        ),
        CheckConstraint(
            """
            tasa_libre_riesgo IS NULL
            OR tasa_libre_riesgo > -100
            """,
            name="ck_configuraciones_tasa_libre_riesgo",
        ),
        CheckConstraint(
            "numero_escenarios BETWEEN 1 AND 1000000",
            name="ck_configuraciones_numero_escenarios",
        ),
        CheckConstraint(
            """
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
            """,
            name="ck_configuraciones_parametros_json",
        ),
        CheckConstraint(
            """
            estado IN (
                'BORRADOR',
                'LISTA',
                'ARCHIVADA'
            )
            """,
            name="ck_configuraciones_estado",
        ),
        CheckConstraint(
            """
            tipo_simulacion <> 'MONTE_CARLO'
            OR numero_escenarios > 1
            """,
            name="ck_configuraciones_monte_carlo",
        ),
        UniqueConstraint(
            "usuario_id",
            "nombre",
            name="uq_configuraciones_usuario_nombre",
        ),
        Index(
            "idx_configuraciones_usuario_estado",
            "usuario_id",
            "estado",
        ),
        Index(
            "idx_configuraciones_portafolio",
            "portafolio_id",
        ),
        Index(
            "idx_configuraciones_tipo_estado",
            "tipo_simulacion",
            "estado",
        ),
        {"schema": "simulation"},
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
            name="fk_configuraciones_usuario",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    portafolio_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "portfolio.portafolios.id",
            name="fk_configuraciones_portafolio",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tipo_simulacion: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    capital_inicial: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    moneda_base: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default=text("'USD'"),
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fecha_fin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    aportacion_periodica: Mapped[Decimal] = (
        mapped_column(
            Numeric(24, 8),
            nullable=False,
            server_default=text("0"),
        )
    )

    frecuencia_aportacion: Mapped[str | None] = (
        mapped_column(
            String(30),
            nullable=True,
        )
    )

    comision_porcentaje: Mapped[Decimal] = (
        mapped_column(
            Numeric(12, 8),
            nullable=False,
            server_default=text("0"),
        )
    )

    inflacion_anual: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(12, 8),
            nullable=True,
        )
    )

    tasa_libre_riesgo: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    numero_escenarios: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    semilla_aleatoria: Mapped[int | None] = (
        mapped_column(
            BigInteger,
            nullable=True,
        )
    )

    parametros: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB(none_as_null=True),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'BORRADOR'"),
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

    portafolio: Mapped[
        PortfolioModel | None
    ] = relationship(
        lazy="joined",
    )

    activos: Mapped[
        list[SimulationConfigurationAssetModel]
    ] = relationship(
        back_populates="configuracion",
        cascade="all, delete-orphan",
        order_by=(
            "SimulationConfigurationAssetModel.orden"
        ),
        lazy="selectin",
    )

    ejecuciones: Mapped[
        list[SimulationExecutionModel]
    ] = relationship(
        back_populates="configuracion",
        lazy="selectin",
    )


class SimulationConfigurationAssetModel(Base):
    __tablename__ = "configuracion_activos"
    __table_args__ = (
        CheckConstraint(
            """
            porcentaje_asignado > 0
            AND porcentaje_asignado <= 100
            """,
            name="ck_configuracion_activos_porcentaje",
        ),
        CheckConstraint(
            """
            monto_inicial IS NULL
            OR monto_inicial >= 0
            """,
            name="ck_configuracion_activos_monto",
        ),
        CheckConstraint(
            """
            precio_inicial IS NULL
            OR precio_inicial >= 0
            """,
            name="ck_configuracion_activos_precio",
        ),
        CheckConstraint(
            "orden > 0",
            name="ck_configuracion_activos_orden",
        ),
        CheckConstraint(
            """
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
            """,
            name="ck_configuracion_activos_parametros",
        ),
        UniqueConstraint(
            "configuracion_id",
            "orden",
            name="uq_configuracion_activos_orden",
        ),
        Index(
            "idx_configuracion_activos_activo",
            "activo_id",
        ),
        {"schema": "simulation"},
    )

    configuracion_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "simulation.configuraciones.id",
            name="fk_configuracion_activos_configuracion",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            name="fk_configuracion_activos_activo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )

    porcentaje_asignado: Mapped[Decimal] = (
        mapped_column(
            Numeric(12, 8),
            nullable=False,
        )
    )

    monto_inicial: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(24, 8),
            nullable=True,
        )
    )

    precio_inicial: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(20, 8),
            nullable=True,
        )
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    parametros: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB(none_as_null=True),
        nullable=True,
    )

    fecha_agregado: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    configuracion: Mapped[
        SimulationConfigurationModel
    ] = relationship(
        back_populates="activos",
    )

    activo: Mapped[AssetModel] = relationship(
        lazy="joined",
    )


class SimulationExecutionModel(Base):
    __tablename__ = "ejecuciones"
    __table_args__ = (
        CheckConstraint(
            """
            estado IN (
                'PENDIENTE',
                'EJECUTANDO',
                'COMPLETADA',
                'FALLIDA',
                'CANCELADA'
            )
            """,
            name="ck_ejecuciones_estado",
        ),
        CheckConstraint(
            "porcentaje_progreso BETWEEN 0 AND 100",
            name="ck_ejecuciones_progreso",
        ),
        CheckConstraint(
            """
            fecha_inicio IS NULL
            OR fecha_inicio >= fecha_solicitud
            """,
            name="ck_ejecuciones_fechas",
        ),
        CheckConstraint(
            """
            fecha_fin IS NULL
            OR (
                fecha_inicio IS NOT NULL
                AND fecha_fin >= fecha_inicio
            )
            """,
            name="ck_ejecuciones_fecha_fin",
        ),
        CheckConstraint(
            """
            estado = 'PENDIENTE'
            OR fecha_inicio IS NOT NULL
            """,
            name="ck_ejecuciones_estado_inicio",
        ),
        CheckConstraint(
            """
            estado NOT IN (
                'COMPLETADA',
                'FALLIDA',
                'CANCELADA'
            )
            OR fecha_fin IS NOT NULL
            """,
            name="ck_ejecuciones_estado_fin",
        ),
        CheckConstraint(
            """
            estado <> 'COMPLETADA'
            OR porcentaje_progreso = 100
            """,
            name="ck_ejecuciones_completada_progreso",
        ),
        CheckConstraint(
            """
            estado <> 'FALLIDA'
            OR NULLIF(TRIM(mensaje_error), '')
               IS NOT NULL
            """,
            name="ck_ejecuciones_error",
        ),
        CheckConstraint(
            """
            parametros_ejecucion IS NULL
            OR jsonb_typeof(parametros_ejecucion)
               = 'object'
            """,
            name="ck_ejecuciones_parametros_json",
        ),
        CheckConstraint(
            """
            identificador_proceso IS NULL
            OR length(trim(identificador_proceso)) > 0
            """,
            name="ck_ejecuciones_identificador",
        ),
        UniqueConstraint(
            "identificador_proceso",
            name="uq_ejecuciones_identificador_proceso",
        ),
        Index(
            "idx_ejecuciones_simulacion_configuracion_fecha",
            "configuracion_id",
            text("fecha_solicitud DESC"),
        ),
        Index(
            "idx_ejecuciones_simulacion_usuario_estado",
            "usuario_id",
            "estado",
        ),
        Index(
            "idx_ejecuciones_simulacion_modelo",
            "version_modelo_id",
        ),
        {"schema": "simulation"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    configuracion_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "simulation.configuraciones.id",
            name="fk_ejecuciones_configuracion",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "app_auth.usuarios.id",
            name="fk_ejecuciones_usuario",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    version_modelo_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.versiones_modelo.id",
            name="fk_ejecuciones_version_modelo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'PENDIENTE'"),
    )

    porcentaje_progreso: Mapped[Decimal] = (
        mapped_column(
            Numeric(7, 4),
            nullable=False,
            server_default=text("0"),
        )
    )

    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_inicio: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )

    fecha_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    mensaje_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parametros_ejecucion: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB(none_as_null=True),
        nullable=True,
    )

    identificador_proceso: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
    )

    configuracion: Mapped[
        SimulationConfigurationModel
    ] = relationship(
        back_populates="ejecuciones",
    )

    usuario: Mapped[UserModel] = relationship(
        lazy="joined",
    )

    version_modelo: Mapped[
        ModelVersionModel | None
    ] = relationship(
        lazy="joined",
    )

    resultado: Mapped[
        SimulationResultModel | None
    ] = relationship(
        back_populates="ejecucion",
        uselist=False,
        lazy="selectin",
    )


class SimulationResultModel(Base):
    __tablename__ = "resultados"
    __table_args__ = (
        CheckConstraint(
            "capital_inicial > 0",
            name="ck_resultados_capital_inicial",
        ),
        CheckConstraint(
            "aportaciones_totales >= 0",
            name="ck_resultados_aportaciones",
        ),
        CheckConstraint(
            "capital_final >= 0",
            name="ck_resultados_capital_final",
        ),
        CheckConstraint(
            """
            volatilidad_anualizada IS NULL
            OR volatilidad_anualizada >= 0
            """,
            name="ck_resultados_volatilidad",
        ),
        CheckConstraint(
            """
            maximo_drawdown_porcentaje IS NULL
            OR maximo_drawdown_porcentaje
               BETWEEN 0 AND 100
            """,
            name="ck_resultados_drawdown",
        ),
        CheckConstraint(
            """
            valor_en_riesgo IS NULL
            OR valor_en_riesgo >= 0
            """,
            name="ck_resultados_var",
        ),
        CheckConstraint(
            """
            nivel_confianza_var IS NULL
            OR nivel_confianza_var BETWEEN 0 AND 1
            """,
            name="ck_resultados_nivel_confianza",
        ),
        CheckConstraint(
            """
            probabilidad_ganancia IS NULL
            OR probabilidad_ganancia BETWEEN 0 AND 1
            """,
            name="ck_resultados_probabilidad_ganancia",
        ),
        CheckConstraint(
            """
            mejor_escenario IS NULL
            OR peor_escenario IS NULL
            OR mejor_escenario >= peor_escenario
            """,
            name="ck_resultados_escenarios",
        ),
        CheckConstraint(
            """
            mediana_escenarios IS NULL
            OR mejor_escenario IS NULL
            OR peor_escenario IS NULL
            OR mediana_escenarios
               BETWEEN peor_escenario
               AND mejor_escenario
            """,
            name="ck_resultados_mediana_escenarios",
        ),
        CheckConstraint(
            """
            moneda = upper(moneda)
            AND moneda ~ '^[A-Z]{3}$'
            """,
            name="ck_resultados_moneda",
        ),
        CheckConstraint(
            """
            resumen IS NULL
            OR jsonb_typeof(resumen) = 'object'
            """,
            name="ck_resultados_resumen_json",
        ),
        UniqueConstraint(
            "ejecucion_id",
            name="uq_resultados_ejecucion",
        ),
        {"schema": "simulation"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    ejecucion_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "simulation.ejecuciones.id",
            name="fk_resultados_ejecucion",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    capital_inicial: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    aportaciones_totales: Mapped[Decimal] = (
        mapped_column(
            Numeric(24, 8),
            nullable=False,
            server_default=text("0"),
        )
    )

    capital_final: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    ganancia_perdida: Mapped[Decimal] = (
        mapped_column(
            Numeric(24, 8),
            nullable=False,
        )
    )

    rendimiento_total_porcentaje: Mapped[
        Decimal
    ] = mapped_column(
        Numeric(16, 8),
        nullable=False,
    )

    rendimiento_anualizado_porcentaje: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    volatilidad_anualizada: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    indice_sharpe: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    maximo_drawdown_porcentaje: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    valor_en_riesgo: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    nivel_confianza_var: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    mejor_escenario: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    peor_escenario: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    mediana_escenarios: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    probabilidad_ganancia: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    resumen: Mapped[
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

    ejecucion: Mapped[SimulationExecutionModel] = (
        relationship(
            back_populates="resultado",
        )
    )

    activos: Mapped[
        list[SimulationAssetResultModel]
    ] = relationship(
        back_populates="resultado",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SimulationAssetResultModel(Base):
    __tablename__ = "resultados_activo"
    __table_args__ = (
        CheckConstraint(
            """
            porcentaje_asignado > 0
            AND porcentaje_asignado <= 100
            """,
            name="ck_resultados_activo_porcentaje",
        ),
        CheckConstraint(
            "capital_asignado >= 0",
            name="ck_resultados_activo_capital",
        ),
        CheckConstraint(
            """
            cantidad_inicial IS NULL
            OR cantidad_inicial >= 0
            """,
            name="ck_resultados_activo_cantidad",
        ),
        CheckConstraint(
            "precio_inicial >= 0",
            name="ck_resultados_activo_precio_inicial",
        ),
        CheckConstraint(
            "precio_final >= 0",
            name="ck_resultados_activo_precio_final",
        ),
        CheckConstraint(
            "valor_final >= 0",
            name="ck_resultados_activo_valor_final",
        ),
        CheckConstraint(
            """
            volatilidad IS NULL
            OR volatilidad >= 0
            """,
            name="ck_resultados_activo_volatilidad",
        ),
        CheckConstraint(
            """
            maximo_drawdown_porcentaje IS NULL
            OR maximo_drawdown_porcentaje
               BETWEEN 0 AND 100
            """,
            name="ck_resultados_activo_drawdown",
        ),
        CheckConstraint(
            """
            detalle IS NULL
            OR jsonb_typeof(detalle) = 'object'
            """,
            name="ck_resultados_activo_detalle_json",
        ),
        UniqueConstraint(
            "resultado_id",
            "activo_id",
            name="uq_resultados_activo",
        ),
        Index(
            "idx_resultados_activo_activo",
            "activo_id",
        ),
        {"schema": "simulation"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    resultado_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "simulation.resultados.id",
            name="fk_resultados_activo_resultado",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            name="fk_resultados_activo_activo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    porcentaje_asignado: Mapped[Decimal] = (
        mapped_column(
            Numeric(12, 8),
            nullable=False,
        )
    )

    capital_asignado: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    cantidad_inicial: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    precio_inicial: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    precio_final: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    valor_final: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    ganancia_perdida: Mapped[Decimal] = (
        mapped_column(
            Numeric(24, 8),
            nullable=False,
        )
    )

    rendimiento_porcentaje: Mapped[Decimal] = (
        mapped_column(
            Numeric(16, 8),
            nullable=False,
        )
    )

    volatilidad: Mapped[Decimal | None] = (
        mapped_column(
            Numeric(16, 8),
            nullable=True,
        )
    )

    maximo_drawdown_porcentaje: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
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

    resultado: Mapped[SimulationResultModel] = (
        relationship(
            back_populates="activos",
        )
    )

    activo: Mapped[AssetModel] = relationship(
        lazy="joined",
    )