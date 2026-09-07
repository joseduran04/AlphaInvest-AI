from datetime import UTC, datetime

import httpx
import pytest

from alphainvest.modules.news.domain.exceptions import (
    NewsProviderRateLimitError,
)
from alphainvest.modules.news.infrastructure.providers.alpha_vantage import (
    AlphaVantageNewsProvider,
)


def build_payload() -> dict[str, object]:
    return {
        "items": "1",
        "feed": [
            {
                "title": "Apple headline",
                "url": "https://example.com/apple",
                "time_published": "20260824T120000",
                "authors": [
                    "Example Author"
                ],
                "summary": "Example summary",
                "banner_image": None,
                "source": "Example Source",
                "category_within_source": (
                    "Markets"
                ),
                "source_domain": (
                    "example.com"
                ),
                "topics": [
                    {
                        "topic": "Technology",
                        "relevance_score": "0.8",
                    }
                ],
                "overall_sentiment_score": 0.2,
                "overall_sentiment_label": (
                    "Somewhat-Bullish"
                ),
                "ticker_sentiment": [
                    {
                        "ticker": "AAPL",
                        "relevance_score": "0.9",
                        "ticker_sentiment_score": "0.3",
                        "ticker_sentiment_label": (
                            "Somewhat-Bullish"
                        ),
                    }
                ],
            }
        ],
    }


@pytest.mark.asyncio
async def test_fetches_and_normalizes_news() -> None:
    async def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        assert (
            request.url.params["function"]
            == "NEWS_SENTIMENT"
        )

        assert (
            request.url.params["tickers"]
            == "AAPL"
        )

        return httpx.Response(
            200,
            json=build_payload(),
        )

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            handler
        )
    )

    provider = AlphaVantageNewsProvider(
        api_key="test-key",
        base_url=(
            "https://www.alphavantage.co"
        ),
        timeout_seconds=15,
        client=client,
    )

    try:
        result = await provider.fetch_news(
            symbol="aapl",
            start_at=None,
            end_at=None,
            limit=1,
        )
    finally:
        await client.aclose()

    assert len(result) == 1

    article = result[0]

    assert article.title == "Apple headline"
    assert article.source == "Example Source"
    assert article.banner_image is None

    assert article.published_at == datetime(
        2026,
        8,
        24,
        12,
        0,
        tzinfo=UTC,
    )

    assert (
        article.ticker_sentiment[0].ticker
        == "AAPL"
    )


@pytest.mark.asyncio
async def test_rejects_rate_limit() -> None:
    async def handler(
        _: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "Note": "API rate limit reached"
            },
        )

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            handler
        )
    )

    provider = AlphaVantageNewsProvider(
        api_key="test-key",
        base_url=(
            "https://www.alphavantage.co"
        ),
        timeout_seconds=15,
        client=client,
    )

    try:
        with pytest.raises(
            NewsProviderRateLimitError
        ):
            await provider.fetch_news(
                symbol="AAPL",
                start_at=None,
                end_at=None,
                limit=1,
            )
    finally:
        await client.aclose()