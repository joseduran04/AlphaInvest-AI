from decimal import Decimal

from alphainvest.modules.ai.domain.temporal_split import (
    TrendTemporalSplit,
)
from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTrainingDataset,
)


class TrendTemporalSplitService:
    """Divide datasets supervisados respetando el orden temporal."""

    @staticmethod
    def split(
        *,
        dataset: TrendTrainingDataset,
        train_ratio: Decimal,
        validation_ratio: Decimal,
    ) -> TrendTemporalSplit:
        TrendTemporalSplitService._validate_ratios(
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )

        purge_sessions = dataset.horizon_sessions

        available_rows = (
            dataset.size
            - (purge_sessions * 2)
        )

        if available_rows < 3:
            raise ValueError(
                "El dataset no contiene suficientes filas "
                "para crear train, validation y test "
                "después de aplicar el purge temporal"
            )

        train_size = int(
            Decimal(available_rows) * train_ratio
        )

        validation_size = int(
            Decimal(available_rows)
            * validation_ratio
        )

        test_size = (
            available_rows
            - train_size
            - validation_size
        )

        if (
            train_size <= 0
            or validation_size <= 0
            or test_size <= 0
        ):
            raise ValueError(
                "La configuración produce una partición vacía"
            )

        train_end = train_size

        validation_start = (
            train_end + purge_sessions
        )
        validation_end = (
            validation_start + validation_size
        )

        test_start = (
            validation_end + purge_sessions
        )

        train_rows = dataset.rows[
            :train_end
        ]

        validation_rows = dataset.rows[
            validation_start:validation_end
        ]

        test_rows = dataset.rows[
            test_start:
        ]

        split = TrendTemporalSplit(
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
            test_ratio=(
                Decimal("1")
                - train_ratio
                - validation_ratio
            ),
            purge_sessions=purge_sessions,
            train=train_rows,
            validation=validation_rows,
            test=test_rows,
        )

        TrendTemporalSplitService._validate_temporal_order(
            split
        )

        return split

    @staticmethod
    def _validate_ratios(
        *,
        train_ratio: Decimal,
        validation_ratio: Decimal,
    ) -> None:
        if train_ratio <= 0:
            raise ValueError(
                "train_ratio debe ser mayor que cero"
            )

        if validation_ratio <= 0:
            raise ValueError(
                "validation_ratio debe ser mayor que cero"
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

    @staticmethod
    def _validate_temporal_order(
        split: TrendTemporalSplit,
    ) -> None:
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