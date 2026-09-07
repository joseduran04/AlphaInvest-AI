from dataclasses import dataclass
from decimal import Decimal

from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)


@dataclass(frozen=True, slots=True)
class SentimentSample:
    text: str
    label: SentimentClass
    provider_score: Decimal
    provider_label: str


@dataclass(frozen=True, slots=True)
class SentimentDataset:
    samples: tuple[
        SentimentSample,
        ...
    ]

    @property
    def size(self) -> int:
        return len(
            self.samples
        )