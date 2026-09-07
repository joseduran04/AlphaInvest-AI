from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.dialects.postgresql import (
    UUID as PostgreSQLUUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from alphainvest.infrastructure.database.base import Base


class AIModelModel(Base):
    """Modelo ORM de ai.modelos_ia."""

    __tablename__ = "modelos_ia"
    __table_args__ = {
        "schema": "ai",
    }

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

    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    objetivo: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'DESARROLLO'"),
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

    versiones: Mapped[list["ModelVersionModel"]] = relationship(
        back_populates="modelo",
    )


class ModelVersionModel(Base):
    """Modelo ORM de ai.versiones_modelo."""

    __tablename__ = "versiones_modelo"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    modelo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.modelos_ia.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    ruta_artefacto: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    checksum: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    algoritmo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    framework: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    hiperparametros: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    metricas: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    conjunto_entrenamiento: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    fecha_entrenamiento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_activacion: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_desactivacion: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    )

    creada_por: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "app_auth.usuarios.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    modelo: Mapped[AIModelModel] = relationship(
        back_populates="versiones",
    )


class AnalysisRequestModel(Base):
    """Modelo ORM de ai.solicitudes_analisis."""

    __tablename__ = "solicitudes_analisis"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
    )

    portafolio_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )

    perfil_riesgo_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )

    ejecucion_simulacion_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
    )

    tipo_analisis: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    horizonte: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    fecha_referencia: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
    )

    parametros: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'PENDIENTE'"),
    )

    porcentaje_progreso: Mapped[
        Decimal
    ] = mapped_column(
        Numeric(7, 4),
        nullable=False,
        server_default=text("0"),
    )

    intentos_procesamiento: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    fecha_solicitud: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_inicio: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_fin: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    mensaje_error: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    identificador_proceso: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
        unique=True,
    )

    fecha_expiracion: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class AssetPredictionModel(Base):
    """Modelo ORM de ai.predicciones_activo."""

    __tablename__ = "predicciones_activo"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    solicitud_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.solicitudes_analisis.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    version_modelo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.versiones_modelo.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    fecha_base: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fecha_objetivo: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    horizonte: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    precio_base: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    precio_predicho: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    precio_minimo_estimado: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    precio_maximo_estimado: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    rendimiento_esperado_porcentaje: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(16, 8),
        nullable=True,
    )

    tendencia: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    confianza: Mapped[Decimal] = mapped_column(
        Numeric(12, 8),
        nullable=False,
    )

    probabilidad_alcista: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    probabilidad_neutral: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    probabilidad_bajista: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    caracteristicas_entrada: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    salida_modelo: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class SentimentAnalysisModel(Base):
    """Modelo ORM de ai.analisis_sentimiento."""

    __tablename__ = "analisis_sentimiento"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    solicitud_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.solicitudes_analisis.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    activo_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    noticia_referencia_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.noticias_referencia.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    version_modelo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.versiones_modelo.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    tipo_fuente: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    identificador_fuente: Mapped[
        str | None
    ] = mapped_column(
        String(200),
        nullable=True,
    )

    sentimiento: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    puntuacion: Mapped[Decimal] = mapped_column(
        Numeric(12, 8),
        nullable=False,
    )

    confianza: Mapped[Decimal] = mapped_column(
        Numeric(12, 8),
        nullable=False,
    )

    probabilidad_positiva: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    probabilidad_neutral: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    probabilidad_negativa: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    relevancia: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    idioma: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    entidades_detectadas: Mapped[
        dict[str, Any] | list[Any] | None
    ] = mapped_column(
        JSONB(
            none_as_null=True
        ),
        nullable=True,
    )

    resumen: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    fecha_contenido: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_analisis: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class RecommendationModel(Base):
    """Modelo ORM de ai.recomendaciones."""

    __tablename__ = "recomendaciones"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    solicitud_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.solicitudes_analisis.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "app_auth.usuarios.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    perfil_riesgo_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.perfiles_riesgo.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    portafolio_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "portfolio.portafolios.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    version_modelo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.versiones_modelo.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    resumen: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    justificacion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    nivel_riesgo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    horizonte: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    confianza: Mapped[Decimal] = mapped_column(
        Numeric(12, 8),
        nullable=False,
    )

    prioridad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'GENERADA'"),
    )

    advertencia: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    parametros: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_expiracion: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_aceptacion: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_rechazo: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class RecommendationAssetModel(Base):
    """Modelo ORM de ai.recomendacion_activos."""

    __tablename__ = "recomendacion_activos"
    __table_args__ = {
        "schema": "ai",
    }

    recomendacion_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.recomendaciones.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    activo_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "market.activos.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        nullable=False,
    )

    accion: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    porcentaje_objetivo: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    precio_referencia: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    precio_objetivo: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    limite_perdida: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    confianza: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    prioridad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    justificacion: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class AnalysisEvidenceModel(Base):
    """Modelo ORM de ai.evidencias_analisis."""

    __tablename__ = "evidencias_analisis"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    solicitud_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.solicitudes_analisis.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    recomendacion_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.recomendaciones.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    prediccion_id: Mapped[
        UUID | None
    ] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.predicciones_activo.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    tipo_evidencia: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    entidad_origen: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    identificador_origen: Mapped[
        str | None
    ] = mapped_column(
        String(200),
        nullable=True,
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    valor_numerico: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    unidad: Mapped[
        str | None
    ] = mapped_column(
        String(30),
        nullable=True,
    )

    peso: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    contribucion: Mapped[
        str | None
    ] = mapped_column(
        String(20),
        nullable=True,
    )

    datos: Mapped[
        dict[str, Any] | None
    ] = mapped_column(
        JSONB,
        nullable=True,
    )

    fecha_evidencia: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )