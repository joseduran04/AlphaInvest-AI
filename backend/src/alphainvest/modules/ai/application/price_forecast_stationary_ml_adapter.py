import numpy as np

from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTrainingRow,
)


class PriceForecastStationaryMLAdapter:
    """Features normalizadas para pronóstico de rendimiento."""

    FEATURE_NAMES = (
        "price_vs_sma_20_pct",
        "price_vs_ema_20_pct",
        "sma_vs_ema_pct",
        "rsi_centered",
        "volatility_30",
        "macd_pct",
        "macd_signal_pct",
        "macd_histogram_pct",
        "log_volume",
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

        targets = np.asarray(
            [
                float(
                    row.target
                    .future_return_percentage
                )
                for row in rows
            ],
            dtype=np.float64,
        )

        features = np.asarray(
            feature_values,
            dtype=np.float64,
        )

        if not np.isfinite(features).all():
            raise ValueError(
                "Las features contienen valores "
                "no finitos"
            )

        if not np.isfinite(targets).all():
            raise ValueError(
                "Los targets contienen valores "
                "no finitos"
            )

        return MLRegressionDataset(
            feature_names=cls.FEATURE_NAMES,
            features=features,
            targets=targets,
        )

    @staticmethod
    def _feature_vector(
        row: PriceForecastTrainingRow,
    ) -> tuple[float, ...]:
        features = row.features

        close = float(features.close)
        sma_20 = float(features.sma_20)
        ema_20 = float(features.ema_20)

        if close <= 0:
            raise ValueError(
                "El precio de cierre debe ser "
                "mayor que cero"
            )

        if sma_20 <= 0 or ema_20 <= 0:
            raise ValueError(
                "SMA y EMA deben ser mayores "
                "que cero"
            )

        volume = (
            float(features.volume)
            if features.volume is not None
            else 0.0
        )

        if volume < 0:
            raise ValueError(
                "El volumen no puede ser negativo"
            )

        price_vs_sma = (
            (close / sma_20) - 1.0
        ) * 100.0

        price_vs_ema = (
            (close / ema_20) - 1.0
        ) * 100.0

        sma_vs_ema = (
            (sma_20 / ema_20) - 1.0
        ) * 100.0

        rsi_centered = (
            float(features.rsi_14) - 50.0
        ) / 50.0

        macd_pct = (
            float(features.macd)
            / close
        ) * 100.0

        macd_signal_pct = (
            float(features.macd_signal)
            / close
        ) * 100.0

        macd_histogram_pct = (
            float(features.macd_histogram)
            / close
        ) * 100.0

        return (
            price_vs_sma,
            price_vs_ema,
            sma_vs_ema,
            rsi_centered,
            float(features.volatility_30),
            macd_pct,
            macd_signal_pct,
            macd_histogram_pct,
            float(np.log1p(volume)),
        )