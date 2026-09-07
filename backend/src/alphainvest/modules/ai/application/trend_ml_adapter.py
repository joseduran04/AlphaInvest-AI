import numpy as np

from alphainvest.modules.ai.domain.ml_dataset import (
    MLClassificationDataset,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTrainingRow,
)


class TrendMLAdapter:
    """Convierte filas de dominio a matrices numéricas de ML."""

    FEATURE_NAMES = (
        "close",
        "volume",
        "sma_20",
        "ema_20",
        "rsi_14",
        "volatility_30",
        "macd",
        "macd_signal",
        "macd_histogram",
    )

    TARGET_ENCODING = {
        TrendClassification.BEARISH: 0,
        TrendClassification.NEUTRAL: 1,
        TrendClassification.BULLISH: 2,
    }

    TARGET_DECODING = {
        value: key
        for key, value in TARGET_ENCODING.items()
    }

    @classmethod
    def transform(
        cls,
        rows: tuple[TrendTrainingRow, ...],
    ) -> MLClassificationDataset:
        if not rows:
            raise ValueError(
                "No existen filas para convertir a matrices ML"
            )

        feature_values = [
            cls._feature_vector(row)
            for row in rows
        ]

        targets = [
            cls.TARGET_ENCODING[
                row.target.classification
            ]
            for row in rows
        ]

        features = np.asarray(
            feature_values,
            dtype=np.float64,
        )

        target_array = np.asarray(
            targets,
            dtype=np.int64,
        )

        if not np.isfinite(features).all():
            raise ValueError(
                "Las features contienen valores no finitos"
            )

        return MLClassificationDataset(
            feature_names=cls.FEATURE_NAMES,
            features=features,
            targets=target_array,
        )

    @staticmethod
    def _feature_vector(
        row: TrendTrainingRow,
    ) -> tuple[float, ...]:
        features = row.features

        volume = (
            float(features.volume)
            if features.volume is not None
            else 0.0
        )

        return (
            float(features.close),
            volume,
            float(features.sma_20),
            float(features.ema_20),
            float(features.rsi_14),
            float(features.volatility_30),
            float(features.macd),
            float(features.macd_signal),
            float(features.macd_histogram),
        )