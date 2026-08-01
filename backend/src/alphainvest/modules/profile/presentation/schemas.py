from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from alphainvest.modules.profile.domain.enums import (
    ClassificationMethod,
    EvaluationStatus,
    RiskClassification,
)


class AnswerOptionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    texto: str
    valor: Decimal
    orden: int


class QuestionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    texto: str
    tipo: str
    orden: int
    ponderacion: Decimal
    obligatoria: bool
    opciones: list[AnswerOptionResponse] = Field(
        default_factory=list,
    )


class QuestionnaireResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    nombre: str
    descripcion: str | None
    version: str
    estado: str
    fecha_publicacion: datetime | None
    preguntas: list[QuestionResponse] = Field(
        default_factory=list,
    )


class EvaluationAnswerRequest(BaseModel):
    question_id: UUID
    option_id: UUID


class CreateRiskEvaluationRequest(BaseModel):
    questionnaire_id: UUID
    answers: list[EvaluationAnswerRequest] = Field(
        min_length=1,
    )


class EvaluationAnswerResponse(BaseModel):
    question_id: UUID
    option_id: UUID | None
    score: Decimal


class RiskEvaluationResponse(BaseModel):
    id: UUID
    questionnaire_id: UUID
    questionnaire_version: str
    raw_score: Decimal
    normalized_score: Decimal
    classification: RiskClassification
    confidence: Decimal | None
    method: ClassificationMethod
    status: EvaluationStatus
    evaluated_at: datetime
    description: str


class CurrentRiskProfileResponse(BaseModel):
    id: UUID
    evaluation_id: UUID
    classification: RiskClassification
    score: Decimal
    confidence: Decimal | None
    description: str
    current: bool
    started_at: datetime


class RiskProfileHistoryItemResponse(BaseModel):
    id: UUID
    evaluation_id: UUID
    classification: RiskClassification
    score: Decimal
    confidence: Decimal | None
    description: str
    current: bool
    started_at: datetime
    ended_at: datetime | None


class RiskProfileHistoryResponse(BaseModel):
    items: list[RiskProfileHistoryItemResponse]
    total: int