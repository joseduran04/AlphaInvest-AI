from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class TrendExperimentConfiguration:
    """Configuración reproducible de un experimento de tendencia."""

    horizon_sessions: int
    neutral_threshold_percentage: Decimal

    train_ratio: Decimal
    validation_ratio: Decimal

    minimum_feature_rows: int

    @property
    def test_ratio(self) -> Decimal:
        return (
            Decimal("1")
            - self.train_ratio
            - self.validation_ratio
        )


PREDICTION_TREND_V1 = TrendExperimentConfiguration(
    horizon_sessions=1,
    neutral_threshold_percentage=Decimal("0.5"),
    train_ratio=Decimal("0.70"),
    validation_ratio=Decimal("0.15"),
    minimum_feature_rows=35,
)


PREDICTION_TREND_YAHOO_V1 = TrendExperimentConfiguration(
    horizon_sessions=5,
    neutral_threshold_percentage=Decimal("2.0"),
    train_ratio=Decimal("0.70"),
    validation_ratio=Decimal("0.15"),
    minimum_feature_rows=500,
)