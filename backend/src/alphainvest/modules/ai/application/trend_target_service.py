from decimal import Decimal

from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTarget,
    TrendTrainingDataset,
    TrendTrainingRow,
)


class TrendTargetService:
    """Genera targets futuros sin introducir fuga temporal."""

    @staticmethod
    def build_training_dataset(
        *,
        dataset: AIFeatureDataset,
        horizon_sessions: int,
        neutral_threshold_percentage: Decimal,
    ) -> TrendTrainingDataset:
        if horizon_sessions <= 0:
            raise ValueError(
                "El horizonte debe ser mayor que cero"
            )

        if neutral_threshold_percentage < 0:
            raise ValueError(
                "El umbral neutral no puede ser negativo"
            )

        if dataset.size <= horizon_sessions:
            raise ValueError(
                "El dataset no contiene suficientes "
                "observaciones para el horizonte solicitado"
            )

        training_rows: list[TrendTrainingRow] = []

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
                    "El precio base debe ser mayor que cero"
                )

            future_return = (
                (
                    target_row.close
                    / base_row.close
                )
                - Decimal("1")
            ) * Decimal("100")

            classification = (
                TrendTargetService._classify(
                    future_return=future_return,
                    neutral_threshold_percentage=(
                        neutral_threshold_percentage
                    ),
                )
            )

            target = TrendTarget(
                base_date=base_row.date,
                target_date=target_row.date,
                base_price=base_row.close,
                target_price=target_row.close,
                future_return_percentage=(
                    future_return
                ),
                classification=classification,
            )

            training_rows.append(
                TrendTrainingRow(
                    features=base_row,
                    target=target,
                )
            )

        return TrendTrainingDataset(
            asset_id=dataset.asset_id,
            horizon_sessions=horizon_sessions,
            neutral_threshold_percentage=(
                neutral_threshold_percentage
            ),
            rows=tuple(training_rows),
        )

    @staticmethod
    def _classify(
        *,
        future_return: Decimal,
        neutral_threshold_percentage: Decimal,
    ) -> TrendClassification:
        if future_return > neutral_threshold_percentage:
            return TrendClassification.BULLISH

        if future_return < (
            -neutral_threshold_percentage
        ):
            return TrendClassification.BEARISH

        return TrendClassification.NEUTRAL