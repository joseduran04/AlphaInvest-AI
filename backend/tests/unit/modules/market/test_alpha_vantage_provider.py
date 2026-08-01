from decimal import Decimal

import httpx
import pytest

from alphainvest.modules.market.domain.exceptions import (
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderResponseError,
)
from alphainvest.modules.market.infrastructure.providers.alpha_vantage import (
    AlphaVantageProvider,
)

pytestmark = pytest.mark.unit


def build_provider(
    payload: dict[str, object],
) -> AlphaVantageProvider:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=payload,
            request=request,
        )

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )

    return AlphaVantageProvider(
        api_key="test-key",
        base_url="https://example.test",
        timeout_seconds=5,
        output_size="compact",
        client=client,
    )


@pytest.mark.asyncio
async def test_provider_normalizes_daily_prices() -> None:
    provider = build_provider(
        {
            "Meta Data": {
                "2. Symbol": "AAPL",
            },
            "Time Series (Daily)": {
                "2026-07-31": {
                    "1. open": "210.00",
                    "2. high": "215.00",
                    "3. low": "208.00",
                    "4. close": "214.50",
                    "5. volume": "1000000",
                },
                "2026-07-30": {
                    "1. open": "205.00",
                    "2. high": "211.00",
                    "3. low": "204.00",
                    "4. close": "210.00",
                    "5. volume": "900000",
                },
            },
        }
    )

    prices = await provider.fetch_daily_prices(
        symbol="aapl",
        currency="usd",
    )

    assert len(prices) == 2
    assert prices[0].date.isoformat() == "2026-07-30"
    assert prices[1].close == Decimal("214.50")
    assert prices[1].currency == "USD"

    assert provider._client is not None
    await provider._client.aclose()


@pytest.mark.asyncio
async def test_provider_requires_api_key() -> None:
    provider = AlphaVantageProvider(
        api_key=None,
        base_url="https://example.test",
        timeout_seconds=5,
    )

    with pytest.raises(
        ProviderConfigurationError,
        match="API key",
    ):
        await provider.fetch_daily_prices(
            symbol="AAPL",
            currency="USD",
        )


@pytest.mark.asyncio
async def test_provider_detects_rate_limit() -> None:
    provider = build_provider(
        {
            "Note": (
                "Thank you for using Alpha Vantage. "
                "Our standard API call frequency is..."
            )
        }
    )

    with pytest.raises(ProviderRateLimitError):
        await provider.fetch_daily_prices(
            symbol="AAPL",
            currency="USD",
        )

    assert provider._client is not None
    await provider._client.aclose()


@pytest.mark.asyncio
async def test_provider_rejects_missing_series() -> None:
    provider = build_provider(
        {
            "Meta Data": {
                "2. Symbol": "AAPL",
            }
        }
    )

    with pytest.raises(
        ProviderResponseError,
        match="serie diaria",
    ):
        await provider.fetch_daily_prices(
            symbol="AAPL",
            currency="USD",
        )

    assert provider._client is not None
    await provider._client.aclose()