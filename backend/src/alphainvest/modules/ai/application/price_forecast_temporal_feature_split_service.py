from decimal import Decimal

from alphainvest.modules.ai.domain.price_forecast_temporal_feature_dataset import (
    PriceForecastTemporalFeatureDataset,
)
from alphainvest.modules.ai.domain.price_forecast_temporal_feature_split import (
    PriceForecastTemporalFeatureSplit,
)


class PriceForecastTemporalFeatureSplitService:
    """Split temporal del experimento V3."""

    @staticmethod
    def split(
        *,
        dataset: PriceForecastTemporalFeatureDataset,
        train_ratio: Decimal,
        validation_ratio: Decimal,
    ) -> PriceForecastTemporalFeatureSplit:
        if train_ratio <= 0:
            raise ValueError(
                "train_ratio debe ser mayor "
                "que cero"
            )

        if validation_ratio <= 0:
            raise ValueError(
                "validation_ratio debe ser mayor "
                "que cero"
            )

        if (
            train_ratio
            + validation_ratio
            >= Decimal("1")
        ):
            raise ValueError(
                "train_ratio + validation_ratio "
                "debe ser menor que uno"
            )

        purge = dataset.horizon_sessions

        available = (
            dataset.size
            - (purge * 2)
        )

        if available < 3:
            raise ValueError(
                "No existen suficientes filas "
                "después del purge"
            )

        train_size = int(
            Decimal(available)
            * train_ratio
        )

        validation_size = int(
            Decimal(available)
            * validation_ratio
        )

        train_end = train_size

        validation_start = (
            train_end + purge
        )

        validation_end = (
            validation_start
            + validation_size
        )

        test_start = (
            validation_end
            + purge
        )

        split = PriceForecastTemporalFeatureSplit(
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
            test_ratio=(
                Decimal("1")
                - train_ratio
                - validation_ratio
            ),
            purge_sessions=purge,
            train=dataset.rows[
                :train_end
            ],
            validation=dataset.rows[
                validation_start:
                validation_end
            ],
            test=dataset.rows[
                test_start:
            ],
        )

        if (
            split.train[-1].target.target_date
            >= split.validation[0].features.date
        ):
            raise ValueError(
                "Existe solapamiento temporal entre "
                "train y validation"
            )

        if (
            split.validation[-1].target.target_date
            >= split.test[0].features.date
        ):
            raise ValueError(
                "Existe solapamiento temporal entre "
                "validation y test"
            )

        return split