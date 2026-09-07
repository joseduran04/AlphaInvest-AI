from datetime import date
from decimal import Decimal
from uuid import UUID

import numpy as np

from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.trend_model_runtime_service import (
    TrendModelRuntimeService,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_prediction import (
    TrendPredictionProbabilities,
    TrendPredictionResult,
)


class TrendInferenceService:
    """Ejecuta inferencias del modelo de tendencia."""

    TARGET_DECODING = {
        0: TrendClassification.BEARISH,
        1: TrendClassification.NEUTRAL,
        2: TrendClassification.BULLISH,
    }

    def __init__(
        self,
        *,
        runtime_service: TrendModelRuntimeService,
        feature_service: AIFeatureDataService,
    ) -> None:
        self._runtime_service = runtime_service
        self._feature_service = feature_service

    async def predict_latest(
        self,
        *,
        version_id: UUID,
        asset_id: UUID,
        start_date: date,
        end_date: date,
    ) -> TrendPredictionResult:
        loaded = await self._runtime_service.load_version(
            version_id=version_id
        )

        dataset = await self._feature_service.build_dataset(
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
        )

        latest = dataset.rows[-1]

        feature_vector = np.asarray(
            [
                [
                    float(latest.close),
                    float(
                        latest.volume
                        if latest.volume is not None
                        else 0
                    ),
                    float(latest.sma_20),
                    float(latest.ema_20),
                    float(latest.rsi_14),
                    float(latest.volatility_30),
                    float(latest.macd),
                    float(latest.macd_signal),
                    float(latest.macd_histogram),
                ]
            ],
            dtype=np.float64,
        )

        probability_values = (
            loaded.classifier.predict_proba(
                feature_vector
            )
        )

        if probability_values.shape != (1, 3):
            raise ValueError(
                "El modelo no devolvió tres "
                "probabilidades de tendencia"
            )

        probabilities = probability_values[0]

        predicted_index = int(
            np.argmax(probabilities)
        )

        classification = self.TARGET_DECODING[
            predicted_index
        ]

        bearish = Decimal(
            str(float(probabilities[0]))
        )
        neutral = Decimal(
            str(float(probabilities[1]))
        )
        bullish = Decimal(
            str(float(probabilities[2]))
        )

        confidence = max(
            bearish,
            neutral,
            bullish,
        )

        return TrendPredictionResult(
            asset_id=asset_id,
            base_date=latest.date,
            version_id=loaded.version_id,
            model_id=loaded.model_id,
            model_version=loaded.version,
            classification=classification,
            confidence=confidence,
            probabilities=TrendPredictionProbabilities(
                bearish=bearish,
                neutral=neutral,
                bullish=bullish,
            ),
        )