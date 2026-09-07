from decimal import Decimal

from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTrainingDataset,
)
from alphainvest.modules.ai.domain.price_forecast_temporal_feature_dataset import (
    PriceForecastTemporalFeatureDataset,
    PriceForecastTemporalFeatureRow,
)


class PriceForecastTemporalFeatureService:
    """Construye features basadas exclusivamente en historia pasada."""

    LOOKBACK_SESSIONS = 20

    @classmethod
    def build_dataset(
        cls,
        *,
        dataset: PriceForecastTrainingDataset,
    ) -> PriceForecastTemporalFeatureDataset:
        if dataset.size <= cls.LOOKBACK_SESSIONS:
            raise ValueError(
                "El dataset no contiene suficientes filas "
                "para construir features temporales"
            )

        temporal_rows: list[
            PriceForecastTemporalFeatureRow
        ] = []

        for index in range(
            cls.LOOKBACK_SESSIONS,
            dataset.size,
        ):
            current = dataset.rows[index]

            previous_1 = dataset.rows[
                index - 1
            ]

            previous_5 = dataset.rows[
                index - 5
            ]

            previous_20 = dataset.rows[
                index - 20
            ]

            return_1d = cls._return_percentage(
                current.features.close,
                previous_1.features.close,
            )

            return_5d = cls._return_percentage(
                current.features.close,
                previous_5.features.close,
            )

            return_20d = cls._return_percentage(
                current.features.close,
                previous_20.features.close,
            )

            momentum_5_20 = (
                return_5d - return_20d
            )

            volume_change_5d = (
                cls._volume_change_percentage(
                    current.features.volume,
                    previous_5.features.volume,
                )
            )

            volume_change_20d = (
                cls._volume_change_percentage(
                    current.features.volume,
                    previous_20.features.volume,
                )
            )

            temporal_rows.append(
                PriceForecastTemporalFeatureRow(
                    base_row=current,
                    return_1d_pct=return_1d,
                    return_5d_pct=return_5d,
                    return_20d_pct=return_20d,
                    momentum_5_20_pct=(
                        momentum_5_20
                    ),
                    volume_change_5d_pct=(
                        volume_change_5d
                    ),
                    volume_change_20d_pct=(
                        volume_change_20d
                    ),
                )
            )

        return PriceForecastTemporalFeatureDataset(
            asset_id=dataset.asset_id,
            horizon_sessions=(
                dataset.horizon_sessions
            ),
            lookback_sessions=(
                cls.LOOKBACK_SESSIONS
            ),
            rows=tuple(temporal_rows),
        )

    @staticmethod
    def _return_percentage(
        current: Decimal,
        previous: Decimal,
    ) -> Decimal:
        if current <= 0 or previous <= 0:
            raise ValueError(
                "Los precios deben ser mayores "
                "que cero"
            )

        return (
            (current / previous)
            - Decimal("1")
        ) * Decimal("100")

    @staticmethod
    def _volume_change_percentage(
        current: Decimal | None,
        previous: Decimal | None,
    ) -> Decimal:
        if (
            current is None
            or previous is None
            or previous <= 0
        ):
            return Decimal("0")

        if current < 0:
            raise ValueError(
                "El volumen no puede ser negativo"
            )

        return (
            (current / previous)
            - Decimal("1")
        ) * Decimal("100")