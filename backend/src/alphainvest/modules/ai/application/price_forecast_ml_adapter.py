import numpy as np

from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTrainingRow,
)


class PriceForecastMLAdapter:
    """Convierte pronósticos a matrices numéricas de regresión."""

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

    @classmethod
    def transform(
        cls,
        rows: tuple[
            PriceForecastTrainingRow,
            ...
        ],
    ) -> MLRegressionDataset:
        if not rows:
            raise ValueError(
                "No existen filas para convertir "
                "a matrices ML"
            )

        feature_values = [
            cls._feature_vector(row)
            for row in rows
        ]

        targets = [
            float(
                row.target
                .future_return_percentage
            )
            for row in rows
        ]

        features = np.asarray(
            feature_values,
            dtype=np.float64,
        )

        target_array = np.asarray(
            targets,
            dtype=np.float64,
        )

        if not np.isfinite(features).all():
            raise ValueError(
                "Las features contienen valores "
                "no finitos"
            )

        if not np.isfinite(target_array).all():
            raise ValueError(
                "Los targets contienen valores "
                "no finitos"
            )

        return MLRegressionDataset(
            feature_names=cls.FEATURE_NAMES,
            features=features,
            targets=target_array,
        )

    @staticmethod
    def _feature_vector(
        row: PriceForecastTrainingRow,
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