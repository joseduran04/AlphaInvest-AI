from dataclasses import dataclass
from decimal import Decimal

from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)


@dataclass(frozen=True, slots=True)
class TrendClassDistribution:
    """Distribución de clases de tendencia."""

    bullish: int
    neutral: int
    bearish: int
    total: int

    def count(
        self,
        classification: TrendClassification,
    ) -> int:
        if classification == TrendClassification.BULLISH:
            return self.bullish

        if classification == TrendClassification.NEUTRAL:
            return self.neutral

        return self.bearish

    def percentage(
        self,
        classification: TrendClassification,
    ) -> Decimal:
        if self.total == 0:
            return Decimal("0")

        return (
            Decimal(self.count(classification))
            / Decimal(self.total)
            * Decimal("100")
        )


@dataclass(frozen=True, slots=True)
class TrendExperimentSpec:
    """Configuración candidata para generar targets."""

    horizon_sessions: int
    neutral_threshold_percentage: Decimal


@dataclass(frozen=True, slots=True)
class TrendExperimentAnalysis:
    """Resultado estadístico de una configuración candidata."""

    specification: TrendExperimentSpec

    total_targets: int
    total_purged: int

    full_distribution: TrendClassDistribution
    train_distribution: TrendClassDistribution
    validation_distribution: TrendClassDistribution
    test_distribution: TrendClassDistribution