from dataclasses import dataclass
from decimal import Decimal

from alphainvest.modules.ai.domain.recommendation_enums import (
    AnalysisEvidenceType,
    EvidenceContribution,
    RecommendationAssetAction,
    RecommendationRiskLevel,
    RecommendationType,
)


@dataclass(frozen=True, slots=True)
class RecommendationEvidenceDecision:
    """Evidencia explicable producida por el motor."""

    evidence_type: AnalysisEvidenceType
    source_entity: str
    source_identifier: str | None
    description: str
    numeric_value: Decimal | None
    unit: str | None
    weight: Decimal | None
    contribution: EvidenceContribution
    data: dict[str, object] | None


@dataclass(frozen=True, slots=True)
class RecommendationAssetDecision:
    """Decisión aplicada al activo analizado."""

    action: RecommendationAssetAction

    target_percentage: Decimal | None

    reference_price: Decimal | None
    target_price: Decimal | None
    loss_limit: Decimal | None

    confidence: Decimal
    priority: int

    justification: str


@dataclass(frozen=True, slots=True)
class RecommendationDecision:
    """Resultado determinístico del motor de recomendación."""

    recommendation_type: RecommendationType

    title: str
    summary: str
    justification: str

    risk_level: RecommendationRiskLevel

    confidence: Decimal

    priority: int

    warning: str

    asset: RecommendationAssetDecision

    evidences: tuple[
        RecommendationEvidenceDecision,
        ...,
    ]

    parameters: dict[str, object] | None