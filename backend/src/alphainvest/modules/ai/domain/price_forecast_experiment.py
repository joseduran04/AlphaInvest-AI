from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PriceForecastExperimentConfiguration:
    """Configuración reproducible del pronóstico de precio."""

    horizon_sessions: int

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


PRICE_FORECAST_YAHOO_V1 = (
    PriceForecastExperimentConfiguration(
        horizon_sessions=5,
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
        minimum_feature_rows=500,
    )
)