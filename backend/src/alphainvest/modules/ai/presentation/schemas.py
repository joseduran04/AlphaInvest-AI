from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisHorizon,
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.domain.enums import (
    AIModelStatus,
)


class AIModelSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str = Field(validation_alias="codigo")
    name: str = Field(validation_alias="nombre")
    type: str = Field(validation_alias="tipo")
    objective: str = Field(validation_alias="objetivo")
    status: AIModelStatus = Field(
        validation_alias="estado"
    )


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_id: UUID = Field(
        validation_alias="modelo_id"
    )
    version: str
    artifact_path: str = Field(
        validation_alias="ruta_artefacto"
    )
    checksum: str
    algorithm: str = Field(
        validation_alias="algoritmo"
    )
    framework: str | None
    hyperparameters: dict[str, Any] | None = Field(
        default=None,
        validation_alias="hiperparametros",
    )
    metrics: dict[str, Any] | None = Field(
        default=None,
        validation_alias="metricas",
    )
    training_dataset: dict[str, Any] | None = Field(
        default=None,
        validation_alias="conjunto_entrenamiento",
    )
    trained_at: datetime = Field(
        validation_alias="fecha_entrenamiento"
    )
    activated_at: datetime | None = Field(
        default=None,
        validation_alias="fecha_activacion",
    )
    deactivated_at: datetime | None = Field(
        default=None,
        validation_alias="fecha_desactivacion",
    )
    active: bool = Field(validation_alias="activa")
    created_by: UUID | None = Field(
        default=None,
        validation_alias="creada_por",
    )
    registered_at: datetime = Field(
        validation_alias="fecha_registro"
    )


class AIModelResponse(AIModelSummaryResponse):
    description: str | None = Field(
        default=None,
        validation_alias="descripcion",
    )
    created_at: datetime = Field(
        validation_alias="fecha_creacion"
    )
    updated_at: datetime = Field(
        validation_alias="fecha_actualizacion"
    )


class AIModelListResponse(BaseModel):
    items: list[AIModelSummaryResponse]
    total: int
    limit: int
    offset: int


class ModelVersionListResponse(BaseModel):
    model_id: UUID
    items: list[ModelVersionResponse]
    total: int


class ActiveModelVersionResponse(BaseModel):
    model: AIModelSummaryResponse
    version: ModelVersionResponse


class AIModelStatusUpdateRequest(BaseModel):
    status: AIModelStatus


class ModelVersionCreateRequest(BaseModel):
    version: str = Field(
        min_length=1,
        max_length=30,
    )
    artifact_path: str = Field(
        min_length=1,
        max_length=1000,
    )
    checksum: str = Field(
        min_length=1,
        max_length=255,
    )
    algorithm: str = Field(
        min_length=1,
        max_length=100,
    )
    framework: str | None = Field(
        default=None,
        max_length=100,
    )
    hyperparameters: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None
    training_dataset: dict[str, Any] | None = None
    trained_at: datetime


class AssetAnalysisRequestCreate(BaseModel):
    asset_id: UUID

    horizon: AnalysisHorizon = (
        AnalysisHorizon.SHORT_TERM
    )

    reference_date: date


class SentimentAnalysisRequestCreate(BaseModel):
    asset_id: UUID
    news_reference_id: UUID
    reference_date: date


class RecommendationRequestCreate(BaseModel):
    asset_id: UUID
    prediction_request_id: UUID

    portfolio_id: UUID | None = None

    horizon: AnalysisHorizon = (
        AnalysisHorizon.SHORT_TERM
    )

    reference_date: date


class IntegralAnalysisRequestCreate(BaseModel):
    asset_id: UUID
    prediction_request_id: UUID

    sentiment_request_ids: list[UUID] = Field(
        default_factory=list
    )

    portfolio_id: UUID | None = None

    horizon: AnalysisHorizon = (
        AnalysisHorizon.SHORT_TERM
    )

    reference_date: date


class AnalysisRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    user_id: UUID = Field(
        validation_alias="usuario_id"
    )

    portfolio_id: UUID | None = Field(
        default=None,
        validation_alias="portafolio_id",
    )

    risk_profile_id: UUID | None = Field(
        default=None,
        validation_alias="perfil_riesgo_id",
    )

    simulation_execution_id: UUID | None = Field(
        default=None,
        validation_alias="ejecucion_simulacion_id",
    )

    analysis_type: AnalysisType = Field(
        validation_alias="tipo_analisis"
    )

    horizon: AnalysisHorizon | None = Field(
        default=None,
        validation_alias="horizonte",
    )

    reference_date: date = Field(
        validation_alias="fecha_referencia"
    )

    parameters: dict[str, Any] | None = Field(
        default=None,
        validation_alias="parametros",
    )

    status: AnalysisRequestStatus = Field(
        validation_alias="estado"
    )

    progress_percentage: Decimal = Field(
        validation_alias="porcentaje_progreso"
    )

    requested_at: datetime = Field(
        validation_alias="fecha_solicitud"
    )

    started_at: datetime | None = Field(
        default=None,
        validation_alias="fecha_inicio",
    )

    finished_at: datetime | None = Field(
        default=None,
        validation_alias="fecha_fin",
    )

    error_message: str | None = Field(
        default=None,
        validation_alias="mensaje_error",
    )

    process_identifier: str | None = Field(
        default=None,
        validation_alias="identificador_proceso",
    )

    expires_at: datetime | None = Field(
        default=None,
        validation_alias="fecha_expiracion",
    )


class AssetPredictionProbabilitiesResponse(
    BaseModel
):
    bullish: Decimal
    neutral: Decimal
    bearish: Decimal


class AssetAnalysisResultResponse(BaseModel):
    request_id: UUID
    asset_id: UUID

    trend_model_version_id: UUID

    price_forecast_version_id: (
        UUID | None
    ) = None

    base_date: date
    target_date: date

    horizon: AnalysisHorizon

    base_price: Decimal
    predicted_price: Decimal

    expected_return_percentage: (
        Decimal | None
    ) = None

    trend: str
    confidence: Decimal

    probabilities: (
        AssetPredictionProbabilitiesResponse
    )

    generated_at: datetime


class RecommendationAssetResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    asset_id: UUID = Field(
        validation_alias="activo_id"
    )

    action: str = Field(
        validation_alias="accion"
    )

    target_percentage: Decimal | None = Field(
        default=None,
        validation_alias="porcentaje_objetivo",
    )

    reference_price: Decimal | None = Field(
        default=None,
        validation_alias="precio_referencia",
    )

    target_price: Decimal | None = Field(
        default=None,
        validation_alias="precio_objetivo",
    )

    loss_limit: Decimal | None = Field(
        default=None,
        validation_alias="limite_perdida",
    )

    confidence: Decimal | None = Field(
        default=None,
        validation_alias="confianza",
    )

    priority: int = Field(
        validation_alias="prioridad"
    )

    justification: str | None = Field(
        default=None,
        validation_alias="justificacion",
    )


class RecommendationEvidenceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    evidence_type: str = Field(
        validation_alias="tipo_evidencia"
    )

    source_entity: str = Field(
        validation_alias="entidad_origen"
    )

    source_identifier: str | None = Field(
        default=None,
        validation_alias="identificador_origen",
    )

    description: str = Field(
        validation_alias="descripcion"
    )

    numeric_value: Decimal | None = Field(
        default=None,
        validation_alias="valor_numerico",
    )

    unit: str | None = Field(
        default=None,
        validation_alias="unidad",
    )

    weight: Decimal | None = Field(
        default=None,
        validation_alias="peso",
    )

    contribution: str | None = Field(
        default=None,
        validation_alias="contribucion",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        validation_alias="datos",
    )

    evidence_date: datetime | None = Field(
        default=None,
        validation_alias="fecha_evidencia",
    )

    registered_at: datetime = Field(
        validation_alias="fecha_registro"
    )


class RecommendationResultResponse(BaseModel):
    request_id: UUID
    recommendation_id: UUID

    user_id: UUID
    asset_id: UUID

    risk_profile_id: UUID | None = None
    portfolio_id: UUID | None = None

    model_version_id: UUID

    type: str
    title: str
    summary: str
    justification: str

    risk_level: str
    horizon: AnalysisHorizon

    confidence: Decimal
    priority: int
    status: str

    warning: str

    parameters: dict[str, Any] | None = None

    generated_at: datetime
    expires_at: datetime | None = None

    assets: list[RecommendationAssetResponse]
    evidence: list[RecommendationEvidenceResponse]