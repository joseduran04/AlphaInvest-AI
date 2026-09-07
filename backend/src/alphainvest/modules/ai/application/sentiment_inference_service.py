from decimal import Decimal
from uuid import UUID

import torch

from alphainvest.modules.ai.application.sentiment_model_runtime_service import (
    SentimentModelRuntimeService,
)
from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)
from alphainvest.modules.ai.domain.sentiment_prediction import (
    SentimentPredictionProbabilities,
    SentimentPredictionResult,
)


class SentimentInferenceService:
    """Ejecuta inferencias NLP de sentimiento financiero."""

    MAX_LENGTH = 96

    TARGET_DECODING = {
        0: SentimentClass.NEGATIVE,
        1: SentimentClass.NEUTRAL,
        2: SentimentClass.POSITIVE,
    }

    def __init__(
        self,
        *,
        runtime_service: SentimentModelRuntimeService,
    ) -> None:
        self._runtime_service = runtime_service

    async def predict(
        self,
        *,
        version_id: UUID,
        text: str,
    ) -> SentimentPredictionResult:
        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError(
                "El texto para análisis de sentimiento "
                "no puede estar vacío"
            )

        loaded = (
            await self._runtime_service
            .load_version(
                version_id=version_id
            )
        )

        encoded = loaded.tokenizer(
            normalized_text,
            truncation=True,
            max_length=self.MAX_LENGTH,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = loaded.classifier(
                **encoded
            )

        logits = outputs.logits

        if tuple(logits.shape) != (1, 3):
            raise ValueError(
                "El modelo no devolvió tres "
                "probabilidades de sentimiento"
            )

        probability_values = (
            torch.softmax(
                logits,
                dim=-1,
            )[0]
            .detach()
            .cpu()
        )

        predicted_index = int(
            torch.argmax(
                probability_values
            ).item()
        )

        classification = (
            self.TARGET_DECODING[
                predicted_index
            ]
        )

        negative = Decimal(
            str(
                float(
                    probability_values[0]
                )
            )
        )

        neutral = Decimal(
            str(
                float(
                    probability_values[1]
                )
            )
        )

        positive = Decimal(
            str(
                float(
                    probability_values[2]
                )
            )
        )

        confidence = max(
            negative,
            neutral,
            positive,
        )

        return SentimentPredictionResult(
            version_id=loaded.version_id,
            model_id=loaded.model_id,
            model_version=loaded.version,
            classification=classification,
            confidence=confidence,
            probabilities=(
                SentimentPredictionProbabilities(
                    negative=negative,
                    neutral=neutral,
                    positive=positive,
                )
            ),
        )