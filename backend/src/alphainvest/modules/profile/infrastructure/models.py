from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from alphainvest.infrastructure.database.base import Base
from alphainvest.modules.ai.infrastructure.models import (
    ModelVersionModel as ModelVersionModel,
)


class QuestionnaireModel(Base):
    __tablename__ = "cuestionarios"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('BORRADOR', 'PUBLICADO', 'INACTIVO')",
            name="ck_cuestionarios_estado",
        ),
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_cuestionarios_nombre_no_vacio",
        ),
        CheckConstraint(
            "estado <> 'PUBLICADO' OR fecha_publicacion IS NOT NULL",
            name="ck_cuestionarios_publicacion",
        ),
        CheckConstraint(
            "length(trim(version)) > 0",
            name="ck_cuestionarios_version_no_vacia",
        ),
        UniqueConstraint(
            "nombre",
            "version",
            name="uq_cuestionarios_nombre_version",
        ),
        Index("idx_cuestionarios_estado", "estado"),
        {"schema": "profile"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    version: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'BORRADOR'"),
    )

    fecha_publicacion: Mapped[datetime | None] = mapped_column(
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

    preguntas: Mapped[list[QuestionModel]] = relationship(
        back_populates="cuestionario",
        cascade="all, delete-orphan",
        order_by="QuestionModel.orden",
        lazy="selectin",
    )

    evaluaciones: Mapped[list[RiskEvaluationModel]] = relationship(
        back_populates="cuestionario",
        lazy="selectin",
    )


class QuestionModel(Base):
    __tablename__ = "preguntas"
    __table_args__ = (
        CheckConstraint(
            "orden > 0",
            name="ck_preguntas_orden",
        ),
        CheckConstraint(
            "ponderacion >= 0",
            name="ck_preguntas_ponderacion",
        ),
        CheckConstraint(
            "length(trim(texto)) > 0",
            name="ck_preguntas_texto_no_vacio",
        ),
        CheckConstraint(
            """
            tipo IN (
                'OPCION_UNICA',
                'OPCION_MULTIPLE',
                'NUMERICA',
                'TEXTO'
            )
            """,
            name="ck_preguntas_tipo",
        ),
        UniqueConstraint(
            "cuestionario_id",
            "orden",
            name="uq_preguntas_cuestionario_orden",
        ),
        Index(
            "idx_preguntas_cuestionario_orden",
            "cuestionario_id",
            "orden",
        ),
        {"schema": "profile"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    cuestionario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.cuestionarios.id",
            name="fk_preguntas_cuestionario",
        ),
        nullable=False,
    )

    texto: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    ponderacion: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        server_default=text("1"),
    )

    obligatoria: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
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

    cuestionario: Mapped[QuestionnaireModel] = relationship(
        back_populates="preguntas",
    )

    opciones: Mapped[list[AnswerOptionModel]] = relationship(
        back_populates="pregunta",
        cascade="all, delete-orphan",
        order_by="AnswerOptionModel.orden",
        lazy="selectin",
    )

    respuestas_usuario: Mapped[list[UserAnswerModel]] = relationship(
        back_populates="pregunta",
        lazy="selectin",
    )


class AnswerOptionModel(Base):
    __tablename__ = "opciones_respuesta"
    __table_args__ = (
        CheckConstraint(
            "orden > 0",
            name="ck_opciones_respuesta_orden",
        ),
        CheckConstraint(
            "length(trim(texto)) > 0",
            name="ck_opciones_respuesta_texto_no_vacio",
        ),
        UniqueConstraint(
            "pregunta_id",
            "orden",
            name="uq_opciones_respuesta_pregunta_orden",
        ),
        Index(
            "idx_opciones_respuesta_pregunta_orden",
            "pregunta_id",
            "orden",
        ),
        {"schema": "profile"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    pregunta_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.preguntas.id",
            name="fk_opciones_respuesta_pregunta",
        ),
        nullable=False,
    )

    texto: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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

    pregunta: Mapped[QuestionModel] = relationship(
        back_populates="opciones",
    )

    respuestas_usuario: Mapped[list[UserAnswerModel]] = relationship(
        back_populates="opcion",
        lazy="selectin",
    )


class RiskEvaluationModel(Base):
    __tablename__ = "evaluaciones_riesgo"
    __table_args__ = (
        CheckConstraint(
            "length(trim(clasificacion)) > 0",
            name="ck_evaluaciones_clasificacion_no_vacia",
        ),
        CheckConstraint(
            "confianza IS NULL OR confianza BETWEEN 0 AND 1",
            name="ck_evaluaciones_confianza",
        ),
        CheckConstraint(
            """
            detalle_calculo IS NULL
            OR jsonb_typeof(detalle_calculo) = 'object'
            """,
            name="ck_evaluaciones_detalle_json",
        ),
        CheckConstraint(
            "estado IN ('COMPLETADA', 'INVALIDA', 'CANCELADA')",
            name="ck_evaluaciones_estado",
        ),
        CheckConstraint(
            """
            metodo_clasificacion IN (
                'REGLAS',
                'INTELIGENCIA_ARTIFICIAL',
                'HIBRIDO'
            )
            """,
            name="ck_evaluaciones_metodo",
        ),
        CheckConstraint(
            """
            metodo_clasificacion = 'REGLAS'
            OR version_modelo_id IS NOT NULL
            """,
            name="ck_evaluaciones_modelo_metodo",
        ),
        CheckConstraint(
            "puntuacion_total >= 0",
            name="ck_evaluaciones_puntuacion_total",
        ),
        CheckConstraint(
            "length(trim(version_cuestionario)) > 0",
            name="ck_evaluaciones_version_no_vacia",
        ),
        Index(
            "idx_evaluaciones_riesgo_cuestionario",
            "cuestionario_id",
        ),
        Index(
            "idx_evaluaciones_riesgo_usuario_fecha",
            "usuario_id",
            text("fecha_evaluacion DESC"),
        ),
        Index(
            "idx_evaluaciones_riesgo_version_modelo",
            "version_modelo_id",
            postgresql_where=text("version_modelo_id IS NOT NULL"),
        ),
        {"schema": "profile"},
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
            name="fk_evaluaciones_riesgo_usuario",
        ),
        nullable=False,
    )

    cuestionario_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.cuestionarios.id",
            name="fk_evaluaciones_riesgo_cuestionario",
        ),
        nullable=False,
    )

    version_cuestionario: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    puntuacion_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )

    clasificacion: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    confianza: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    metodo_clasificacion: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    version_modelo_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "ai.versiones_modelo.id",
            name="fk_evaluaciones_riesgo_version_modelo",
        ),
        nullable=True,
    )

    fecha_evaluacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'COMPLETADA'"),
    )

    detalle_calculo: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    cuestionario: Mapped[QuestionnaireModel] = relationship(
        back_populates="evaluaciones",
    )

    respuestas: Mapped[list[UserAnswerModel]] = relationship(
        back_populates="evaluacion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    perfil_riesgo: Mapped[RiskProfileModel | None] = relationship(
        back_populates="evaluacion",
        uselist=False,
        lazy="selectin",
    )


class UserAnswerModel(Base):
    __tablename__ = "respuestas_usuario"
    __table_args__ = (
        CheckConstraint(
            """
            opcion_id IS NOT NULL
            OR valor_numerico IS NOT NULL
            OR NULLIF(trim(respuesta_texto), '') IS NOT NULL
            """,
            name="ck_respuestas_usuario_contenido",
        ),
        CheckConstraint(
            "puntuacion_obtenida >= 0",
            name="ck_respuestas_usuario_puntuacion",
        ),
        UniqueConstraint(
            "evaluacion_id",
            "pregunta_id",
            name="uq_respuestas_usuario_evaluacion_pregunta",
        ),
        Index(
            "idx_respuestas_usuario_pregunta",
            "pregunta_id",
        ),
        Index(
            "idx_respuestas_usuario_opcion",
            "opcion_id",
            postgresql_where=text("opcion_id IS NOT NULL"),
        ),
        {"schema": "profile"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    evaluacion_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.evaluaciones_riesgo.id",
            name="fk_respuestas_usuario_evaluacion",
        ),
        nullable=False,
    )

    pregunta_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.preguntas.id",
            name="fk_respuestas_usuario_pregunta",
        ),
        nullable=False,
    )

    opcion_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.opciones_respuesta.id",
            name="fk_respuestas_usuario_opcion",
        ),
        nullable=True,
    )

    valor_numerico: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 6),
        nullable=True,
    )

    respuesta_texto: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    puntuacion_obtenida: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        server_default=text("0"),
    )

    fecha_respuesta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    evaluacion: Mapped[RiskEvaluationModel] = relationship(
        back_populates="respuestas",
    )

    pregunta: Mapped[QuestionModel] = relationship(
        back_populates="respuestas_usuario",
    )

    opcion: Mapped[AnswerOptionModel | None] = relationship(
        back_populates="respuestas_usuario",
    )


class RiskProfileModel(Base):
    __tablename__ = "perfiles_riesgo"
    __table_args__ = (
        CheckConstraint(
            """
            clasificacion IN (
                'CONSERVADOR',
                'MODERADO_CONSERVADOR',
                'MODERADO',
                'MODERADO_AGRESIVO',
                'AGRESIVO'
            )
            """,
            name="ck_perfiles_riesgo_clasificacion",
        ),
        CheckConstraint(
            "confianza IS NULL OR confianza BETWEEN 0 AND 1",
            name="ck_perfiles_riesgo_confianza",
        ),
        CheckConstraint(
            "length(trim(descripcion)) > 0",
            name="ck_perfiles_riesgo_descripcion",
        ),
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_fin >= fecha_inicio",
            name="ck_perfiles_riesgo_fechas",
        ),
        CheckConstraint(
            "puntuacion >= 0",
            name="ck_perfiles_riesgo_puntuacion",
        ),
        CheckConstraint(
            "(vigente = true AND fecha_fin IS NULL) OR vigente = false",
            name="ck_perfiles_riesgo_vigencia",
        ),
        UniqueConstraint(
            "evaluacion_id",
            name="uq_perfiles_riesgo_evaluacion",
        ),
        Index(
            "idx_perfiles_riesgo_usuario_fecha",
            "usuario_id",
            text("fecha_inicio DESC"),
        ),
        Index(
            "idx_perfiles_riesgo_clasificacion",
            "clasificacion",
            postgresql_where=text("vigente = true"),
        ),
        Index(
            "uq_perfil_vigente_usuario",
            "usuario_id",
            unique=True,
            postgresql_where=text("vigente = true"),
        ),
        {"schema": "profile"},
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
            name="fk_perfiles_riesgo_usuario",
        ),
        nullable=False,
    )

    evaluacion_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "profile.evaluaciones_riesgo.id",
            name="fk_perfiles_riesgo_evaluacion",
        ),
        nullable=False,
    )

    clasificacion: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    puntuacion: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )

    confianza: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    vigente: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_fin: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    evaluacion: Mapped[RiskEvaluationModel] = relationship(
        back_populates="perfil_riesgo",
    )