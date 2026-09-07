from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128

from alphainvest.modules.ai.domain.sentiment_dataset import (
    SentimentDataset,
    SentimentSample,
)
from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)


class SentimentDatasetService:
    """Construye dataset NLP desde documentos News."""

    @classmethod
    def build(
        cls,
        documents: Iterable[
            dict[str, Any]
        ],
    ) -> SentimentDataset:
        samples: list[
            SentimentSample
        ] = []

        for document in documents:
            sample = cls._build_sample(
                document
            )

            if sample is not None:
                samples.append(
                    sample
                )

        return SentimentDataset(
            samples=tuple(
                samples
            )
        )

    @classmethod
    def _build_sample(
        cls,
        document: dict[str, Any],
    ) -> SentimentSample | None:
        title = cls._text(
            document.get("title")
        )

        summary = cls._text(
            document.get("summary")
        )

        text = " ".join(
            part
            for part in (
                title,
                summary,
            )
            if part
        ).strip()

        if not text:
            return None

        provider_sentiment = (
            document.get(
                "provider_sentiment"
            )
        )

        if not isinstance(
            provider_sentiment,
            dict,
        ):
            return None

        score = cls._decimal(
            provider_sentiment.get(
                "score"
            )
        )

        label = cls._text(
            provider_sentiment.get(
                "label"
            )
        )

        if (
            score is None
            or label is None
        ):
            return None

        sentiment_class = (
            cls._map_provider_label(
                label
            )
        )

        if sentiment_class is None:
            return None

        return SentimentSample(
            text=text,
            label=sentiment_class,
            provider_score=score,
            provider_label=label,
        )

    @staticmethod
    def _map_provider_label(
        label: str,
    ) -> SentimentClass | None:
        normalized = (
            label.strip().lower()
        )

        if "bullish" in normalized:
            return SentimentClass.POSITIVE

        if "bearish" in normalized:
            return SentimentClass.NEGATIVE

        if "neutral" in normalized:
            return SentimentClass.NEUTRAL

        return None

    @staticmethod
    def _text(
        value: object,
    ) -> str | None:
        if not isinstance(
            value,
            str,
        ):
            return None

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _decimal(
        value: object,
    ) -> Decimal | None:
        if isinstance(
            value,
            Decimal128,
        ):
            return value.to_decimal()

        if isinstance(
            value,
            Decimal,
        ):
            return value

        if isinstance(
            value,
            int | float | str,
        ):
            try:
                return Decimal(
                    str(value)
                )
            except Exception:
                return None

        return None