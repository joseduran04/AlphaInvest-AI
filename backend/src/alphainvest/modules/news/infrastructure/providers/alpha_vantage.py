from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from alphainvest.modules.news.domain.exceptions import (
    NewsProviderConfigurationError,
    NewsProviderRateLimitError,
    NewsProviderRequestError,
    NewsProviderResponseError,
)
from alphainvest.modules.news.domain.news_document import (
    NewsDocument,
    NewsTickerSentiment,
    NewsTopic,
)


class AlphaVantageNewsProvider:
    """Adaptador para Alpha Vantage NEWS_SENTIMENT."""

    source_name = "Alpha Vantage"

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        timeout_seconds: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = (
            api_key.strip()
            if api_key is not None
            else None
        )
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._client = client

    async def fetch_news(
        self,
        *,
        symbol: str,
        start_at: datetime | None,
        end_at: datetime | None,
        limit: int,
    ) -> list[NewsDocument]:
        if not self._api_key:
            raise NewsProviderConfigurationError(
                "No se configuró la API key de Alpha Vantage"
            )

        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise NewsProviderConfigurationError(
                "El símbolo financiero no puede estar vacío"
            )

        if limit < 1:
            raise NewsProviderConfigurationError(
                "El límite de noticias debe ser mayor que cero"
            )

        params: dict[str, str] = {
            "function": "NEWS_SENTIMENT",
            "tickers": normalized_symbol,
            "apikey": self._api_key,
        }

        if start_at is not None:
            params["time_from"] = self._format_datetime(
                start_at
            )

        if end_at is not None:
            params["time_to"] = self._format_datetime(
                end_at
            )

        payload = await self._request(
            params=params
        )

        self._validate_provider_response(
            payload
        )

        raw_feed = payload.get("feed")

        if not isinstance(raw_feed, list):
            raise NewsProviderResponseError(
                "Alpha Vantage no devolvió una lista de noticias"
            )

        documents = [
            self._parse_article(article)
            for article in raw_feed
        ]

        return documents[:limit]

    async def _request(
        self,
        *,
        params: dict[str, str],
    ) -> dict[str, Any]:
        try:
            if self._client is not None:
                response = await self._client.get(
                    f"{self._base_url}/query",
                    params=params,
                    timeout=self._timeout_seconds,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self._base_url}/query",
                        params=params,
                        timeout=self._timeout_seconds,
                    )

            response.raise_for_status()

        except httpx.TimeoutException as error:
            raise NewsProviderRequestError(
                "Alpha Vantage excedió el tiempo de espera"
            ) from error

        except httpx.HTTPStatusError as error:
            raise NewsProviderRequestError(
                "Alpha Vantage devolvió un estado HTTP "
                f"{error.response.status_code}"
            ) from error

        except httpx.RequestError as error:
            raise NewsProviderRequestError(
                "No fue posible conectar con Alpha Vantage"
            ) from error

        try:
            payload = response.json()
        except ValueError as error:
            raise NewsProviderResponseError(
                "Alpha Vantage devolvió JSON inválido"
            ) from error

        if not isinstance(payload, dict):
            raise NewsProviderResponseError(
                "Alpha Vantage devolvió una estructura inválida"
            )

        return payload

    @staticmethod
    def _validate_provider_response(
        payload: dict[str, Any],
    ) -> None:
        note = payload.get("Note")

        if isinstance(note, str):
            raise NewsProviderRateLimitError(
                "Alpha Vantage alcanzó su límite de consultas"
            )

        information = payload.get(
            "Information"
        )

        if isinstance(information, str):
            lowered = information.lower()

            if (
                "rate limit" in lowered
                or "frequency" in lowered
            ):
                raise NewsProviderRateLimitError(
                    "Alpha Vantage alcanzó su límite de consultas"
                )

            raise NewsProviderResponseError(
                information
            )

        error_message = payload.get(
            "Error Message"
        )

        if isinstance(error_message, str):
            raise NewsProviderResponseError(
                error_message
            )

    @classmethod
    def _parse_article(
        cls,
        raw_article: object,
    ) -> NewsDocument:
        if not isinstance(
            raw_article,
            dict,
        ):
            raise NewsProviderResponseError(
                "Alpha Vantage devolvió una noticia inválida"
            )

        try:
            title = cls._required_string(
                raw_article,
                "title",
            )
            url = cls._required_string(
                raw_article,
                "url",
            )
            summary = cls._required_string(
                raw_article,
                "summary",
            )
            source = cls._required_string(
                raw_article,
                "source",
            )

            published_at = (
                cls._parse_published_at(
                    cls._required_string(
                        raw_article,
                        "time_published",
                    )
                )
            )

            authors = cls._parse_authors(
                raw_article.get(
                    "authors"
                )
            )

            topics = cls._parse_topics(
                raw_article.get(
                    "topics"
                )
            )

            ticker_sentiment = (
                cls._parse_ticker_sentiment(
                    raw_article.get(
                        "ticker_sentiment"
                    )
                )
            )

            provider_score = (
                cls._optional_decimal(
                    raw_article.get(
                        "overall_sentiment_score"
                    )
                )
            )

            provider_label = (
                cls._optional_string(
                    raw_article.get(
                        "overall_sentiment_label"
                    )
                )
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            InvalidOperation,
        ) as error:
            raise NewsProviderResponseError(
                "Alpha Vantage devolvió campos de noticia inválidos"
            ) from error

        return NewsDocument(
            title=title,
            url=url,
            published_at=published_at,
            authors=authors,
            summary=summary,
            banner_image=cls._optional_string(
                raw_article.get(
                    "banner_image"
                )
            ),
            source=source,
            category_within_source=(
                cls._optional_string(
                    raw_article.get(
                        "category_within_source"
                    )
                )
            ),
            source_domain=cls._optional_string(
                raw_article.get(
                    "source_domain"
                )
            ),
            topics=topics,
            provider_sentiment_score=(
                provider_score
            ),
            provider_sentiment_label=(
                provider_label
            ),
            ticker_sentiment=ticker_sentiment,
            raw_payload=dict(raw_article),
        )

    @staticmethod
    def _required_string(
        payload: dict[str, Any],
        key: str,
    ) -> str:
        value = payload[key]

        if not isinstance(value, str):
            raise TypeError(key)

        normalized = value.strip()

        if not normalized:
            raise ValueError(key)

        return normalized

    @staticmethod
    def _optional_string(
        value: object,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _optional_decimal(
        value: object,
    ) -> Decimal | None:
        if value is None:
            return None

        return Decimal(
            str(value)
        )

    @staticmethod
    def _parse_published_at(
        value: str,
    ) -> datetime:
        parsed = datetime.strptime(
            value,
            "%Y%m%dT%H%M%S",
        )

        return parsed.replace(
            tzinfo=UTC
        )

    @staticmethod
    def _parse_authors(
        raw_authors: object,
    ) -> tuple[str, ...]:
        if not isinstance(
            raw_authors,
            list,
        ):
            raise TypeError

        authors: list[str] = []

        for raw_author in raw_authors:
            if not isinstance(
                raw_author,
                str,
            ):
                raise TypeError

            normalized = (
                raw_author.strip()
            )

            if normalized:
                authors.append(
                    normalized
                )

        return tuple(authors)

    @classmethod
    def _parse_topics(
        cls,
        raw_topics: object,
    ) -> tuple[NewsTopic, ...]:
        if not isinstance(
            raw_topics,
            list,
        ):
            raise TypeError

        topics: list[NewsTopic] = []

        for raw_topic in raw_topics:
            if not isinstance(
                raw_topic,
                dict,
            ):
                raise TypeError

            topics.append(
                NewsTopic(
                    topic=cls._required_string(
                        raw_topic,
                        "topic",
                    ),
                    relevance_score=Decimal(
                        str(
                            raw_topic[
                                "relevance_score"
                            ]
                        )
                    ),
                )
            )

        return tuple(topics)

    @classmethod
    def _parse_ticker_sentiment(
        cls,
        raw_items: object,
    ) -> tuple[
        NewsTickerSentiment,
        ...,
    ]:
        if not isinstance(
            raw_items,
            list,
        ):
            raise TypeError

        items: list[
            NewsTickerSentiment
        ] = []

        for raw_item in raw_items:
            if not isinstance(
                raw_item,
                dict,
            ):
                raise TypeError

            items.append(
                NewsTickerSentiment(
                    ticker=cls._required_string(
                        raw_item,
                        "ticker",
                    ).upper(),
                    relevance_score=Decimal(
                        str(
                            raw_item[
                                "relevance_score"
                            ]
                        )
                    ),
                    sentiment_score=Decimal(
                        str(
                            raw_item[
                                "ticker_sentiment_score"
                            ]
                        )
                    ),
                    sentiment_label=(
                        cls._required_string(
                            raw_item,
                            "ticker_sentiment_label",
                        )
                    ),
                )
            )

        return tuple(items)

    @staticmethod
    def _format_datetime(
        value: datetime,
    ) -> str:
        normalized = value.astimezone(
            UTC
        )

        return normalized.strftime(
            "%Y%m%dT%H%M"
        )