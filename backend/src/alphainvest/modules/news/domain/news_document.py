from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class NewsTopic:
    topic: str
    relevance_score: Decimal


@dataclass(frozen=True, slots=True)
class NewsTickerSentiment:
    ticker: str
    relevance_score: Decimal
    sentiment_score: Decimal
    sentiment_label: str


@dataclass(frozen=True, slots=True)
class NewsDocument:
    title: str
    url: str
    published_at: datetime
    authors: tuple[str, ...]
    summary: str
    banner_image: str | None
    source: str
    category_within_source: str | None
    source_domain: str | None
    topics: tuple[NewsTopic, ...]
    provider_sentiment_score: Decimal | None
    provider_sentiment_label: str | None
    ticker_sentiment: tuple[
        NewsTickerSentiment,
        ...
    ]
    raw_payload: dict[str, Any]