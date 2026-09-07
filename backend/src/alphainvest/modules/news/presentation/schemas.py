from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class NewsTopicResponse(BaseModel):
    topic: str
    relevance_score: Decimal


class NewsTickerSentimentResponse(BaseModel):
    ticker: str
    relevance_score: Decimal
    sentiment_score: Decimal
    sentiment_label: str


class NewsProviderSentimentResponse(BaseModel):
    score: Decimal | None
    label: str | None


class NewsResponse(BaseModel):
    reference_id: UUID
    asset_id: UUID
    mongo_document_id: str

    title: str
    source: str
    url: str | None
    published_at: datetime

    language: str | None
    relevance: Decimal | None

    authors: list[str]
    summary: str
    banner_image: str | None
    category_within_source: str | None
    source_domain: str | None

    topics: list[NewsTopicResponse]

    provider_sentiment: (
        NewsProviderSentimentResponse
    )

    ticker_sentiment: list[
        NewsTickerSentimentResponse
    ]


class NewsListResponse(BaseModel):
    asset_id: UUID
    items: list[NewsResponse]
    total: int
    limit: int
    offset: int
    start_at: datetime | None
    end_at: datetime | None


class NewsSynchronizationResponse(
    BaseModel
):
    execution_id: UUID

    asset_id: UUID
    symbol: str

    source_id: UUID
    source_name: str

    received: int
    created: int
    reused: int
    failed: int

    synchronized_at: datetime