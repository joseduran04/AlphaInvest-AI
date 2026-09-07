from decimal import Decimal

from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTarget,
    PriceForecastTrainingDataset,
    PriceForecastTrainingRow,
)


class PriceForecastTargetService:
    """Genera targets continuos sin fuga temporal."""

    @staticmethod
    def build_training_dataset(
        *,
        dataset: AIFeatureDataset,
        horizon_sessions: int,
    ) -> PriceForecastTrainingDataset:
        if horizon_sessions <= 0:
            raise ValueError(
                "El horizonte debe ser mayor que cero"
            )

        if dataset.size <= horizon_sessions:
            raise ValueError(
                "El dataset no contiene suficientes "
                "observaciones para el horizonte solicitado"
            )

        training_rows: list[
            PriceForecastTrainingRow
        ] = []

        last_base_index = (
            dataset.size - horizon_sessions
        )

        for index in range(last_base_index):
            base_row = dataset.rows[index]

            target_row = dataset.rows[
                index + horizon_sessions
            ]

            if base_row.close <= 0:
                raise ValueError(
                    "El precio base debe ser "
                    "mayor que cero"
                )

            future_return = (
                (
                    target_row.close
                    / base_row.close
                )
                - Decimal("1")
            ) * Decimal("100")

            target = PriceForecastTarget(
                base_date=base_row.date,
                target_date=target_row.date,
                base_price=base_row.close,
                target_price=target_row.close,
                future_return_percentage=(
                    future_return
                ),
            )

            training_rows.append(
                PriceForecastTrainingRow(
                    features=base_row,
                    target=target,
                )
            )

        return PriceForecastTrainingDataset(
            asset_id=dataset.asset_id,
            horizon_sessions=horizon_sessions,
            rows=tuple(training_rows),
        )