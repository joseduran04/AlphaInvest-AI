import numpy as np

from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)
from alphainvest.modules.ai.domain.price_forecast_temporal_feature_dataset import (
    PriceForecastTemporalFeatureRow,
)


class PriceForecastTemporalMLAdapter:
    """Convierte features temporales V3 a matrices ML."""

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
        "return_1d_pct",
        "return_5d_pct",
        "return_20d_pct",
        "momentum_5_20_pct",
        "volume_change_5d_pct",
        "volume_change_20d_pct",
    )

    @classmethod
    def transform(
        cls,
        rows: tuple[
            PriceForecastTemporalFeatureRow,
            ...
        ],
    ) -> MLRegressionDataset:
        if not rows:
            raise ValueError(
                "No existen filas para convertir "
                "a matrices ML"
            )

        features = np.asarray(
            [
                cls._feature_vector(row)
                for row in rows
            ],
            dtype=np.float64,
        )

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
        row: PriceForecastTemporalFeatureRow,
    ) -> tuple[float, ...]:
        source = row.features

        close = float(source.close)
        sma_20 = float(source.sma_20)
        ema_20 = float(source.ema_20)

        if close <= 0:
            raise ValueError(
                "El precio debe ser mayor que cero"
            )

        if sma_20 <= 0 or ema_20 <= 0:
            raise ValueError(
                "SMA y EMA deben ser mayores "
                "que cero"
            )

        volume = (
            float(source.volume)
            if source.volume is not None
            else 0.0
        )

        if volume < 0:
            raise ValueError(
                "El volumen no puede ser negativo"
            )

        return (
            ((close / sma_20) - 1.0)
            * 100.0,
            ((close / ema_20) - 1.0)
            * 100.0,
            ((sma_20 / ema_20) - 1.0)
            * 100.0,
            (
                float(source.rsi_14)
                - 50.0
            ) / 50.0,
            float(source.volatility_30),
            (
                float(source.macd)
                / close
            ) * 100.0,
            (
                float(source.macd_signal)
                / close
            ) * 100.0,
            (
                float(source.macd_histogram)
                / close
            ) * 100.0,
            float(np.log1p(volume)),
            float(row.return_1d_pct),
            float(row.return_5d_pct),
            float(row.return_20d_pct),
            float(row.momentum_5_20_pct),
            float(row.volume_change_5d_pct),
            float(row.volume_change_20d_pct),
        )