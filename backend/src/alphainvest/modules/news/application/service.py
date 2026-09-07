from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from bson.decimal128 import Decimal128

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
)
from alphainvest.modules.market.infrastructure.models import (
    NewsReferenceModel,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.domain.exceptions import (
    InvalidNewsDateRangeError,
    NewsDocumentNotFoundError,
)
from alphainvest.modules.news.infrastructure.mongodb_repository import (
    MongoNewsRepository,
)
from alphainvest.modules.news.presentation.schemas import (
    NewsListResponse,
    NewsProviderSentimentResponse,
    NewsResponse,
    NewsTickerSentimentResponse,
    NewsTopicResponse,
)


class NewsService:
    """Casos de uso de consulta de noticias."""

    def __init__(
        self,
        *,
        market_repository: MarketRepository,
        mongo_repository: MongoNewsRepository,
    ) -> None:
        self._market_repository = (
            market_repository
        )

        self._mongo_repository = (
            mongo_repository
        )

    async def list_asset_news(
        self,
        *,
        asset_id: UUID,
        start_at: datetime | None,
        end_at: datetime | None,
        limit: int,
        offset: int,
    ) -> NewsListResponse:
        if (
            start_at is not None
            and end_at is not None
            and start_at > end_at
        ):
            raise InvalidNewsDateRangeError(
                "La fecha inicial no puede "
                "ser posterior a la fecha final"
            )

        asset = (
            await self._market_repository
            .get_asset(asset_id)
        )

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        references, total = (
            await self._market_repository
            .list_news_references(
                asset_id=asset_id,
                start_at=start_at,
                end_at=end_at,
                limit=limit,
                offset=offset,
            )
        )

        items: list[NewsResponse] = []

        for reference in references:
            document = (
                await self._mongo_repository
                .get_by_document_id(
                    reference.mongo_document_id
                )
            )

            if document is None:
                raise NewsDocumentNotFoundError(
                    "La referencia PostgreSQL "
                    "no tiene documento MongoDB"
                )

            items.append(
                self._build_response(
                    reference=reference,
                    document=document,
                )
            )

        return NewsListResponse(
            asset_id=asset_id,
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            start_at=start_at,
            end_at=end_at,
        )

    @classmethod
    def _build_response(
        cls,
        *,
        reference: NewsReferenceModel,
        document: dict[str, Any],
    ) -> NewsResponse:
        authors = cls._string_list(
            document.get("authors")
        )

        topics = cls._topics(
            document.get("topics")
        )

        ticker_sentiment = (
            cls._ticker_sentiment(
                document.get(
                    "ticker_sentiment"
                )
            )
        )

        provider_sentiment = (
            cls._provider_sentiment(
                document.get(
                    "provider_sentiment"
                )
            )
        )

        summary = document.get(
            "summary"
        )

        if not isinstance(
            summary,
            str,
        ):
            raise NewsDocumentNotFoundError(
                "El documento MongoDB "
                "no contiene un resumen válido"
            )

        return NewsResponse(
            reference_id=reference.id,
            asset_id=reference.activo_id,
            mongo_document_id=(
                reference.mongo_document_id
            ),
            title=reference.titulo,
            source=reference.fuente,
            url=reference.url,
            published_at=(
                reference.fecha_publicacion
            ),
            language=reference.idioma,
            relevance=reference.relevancia,
            authors=authors,
            summary=summary,
            banner_image=(
                cls._optional_string(
                    document.get(
                        "banner_image"
                    )
                )
            ),
            category_within_source=(
                cls._optional_string(
                    document.get(
                        "category_within_source"
                    )
                )
            ),
            source_domain=(
                cls._optional_string(
                    document.get(
                        "source_domain"
                    )
                )
            ),
            topics=topics,
            provider_sentiment=(
                provider_sentiment
            ),
            ticker_sentiment=(
                ticker_sentiment
            ),
        )

    @staticmethod
    def _string_list(
        value: object,
    ) -> list[str]:
        if not isinstance(
            value,
            list,
        ):
            return []

        return [
            item
            for item in value
            if isinstance(item, str)
        ]

    @classmethod
    def _topics(
        cls,
        value: object,
    ) -> list[NewsTopicResponse]:
        if not isinstance(
            value,
            list,
        ):
            return []

        items: list[
            NewsTopicResponse
        ] = []

        for raw_item in value:
            if not isinstance(
                raw_item,
                dict,
            ):
                continue

            topic = raw_item.get(
                "topic"
            )

            relevance = raw_item.get(
                "relevance_score"
            )

            if not isinstance(
                topic,
                str,
            ):
                continue

            relevance_decimal = (
                cls._decimal_value(
                    relevance
                )
            )

            if relevance_decimal is None:
                continue

            items.append(
                NewsTopicResponse(
                    topic=topic,
                    relevance_score=(
                        relevance_decimal
                    ),
                )
            )

        return items

    @classmethod
    def _ticker_sentiment(
        cls,
        value: object,
    ) -> list[
        NewsTickerSentimentResponse
    ]:
        if not isinstance(
            value,
            list,
        ):
            return []

        items: list[
            NewsTickerSentimentResponse
        ] = []

        for raw_item in value:
            if not isinstance(
                raw_item,
                dict,
            ):
                continue

            ticker = raw_item.get(
                "ticker"
            )

            relevance = cls._decimal_value(
                raw_item.get(
                    "relevance_score"
                )
            )

            sentiment = cls._decimal_value(
                raw_item.get(
                    "sentiment_score"
                )
            )

            label = raw_item.get(
                "sentiment_label"
            )

            if (
                not isinstance(ticker, str)
                or relevance is None
                or sentiment is None
                or not isinstance(label, str)
            ):
                continue

            items.append(
                NewsTickerSentimentResponse(
                    ticker=ticker,
                    relevance_score=relevance,
                    sentiment_score=sentiment,
                    sentiment_label=label,
                )
            )

        return items

    @classmethod
    def _provider_sentiment(
        cls,
        value: object,
    ) -> NewsProviderSentimentResponse:
        if not isinstance(
            value,
            dict,
        ):
            return (
                NewsProviderSentimentResponse(
                    score=None,
                    label=None,
                )
            )

        label = value.get(
            "label"
        )

        return NewsProviderSentimentResponse(
            score=cls._decimal_value(
                value.get("score")
            ),
            label=(
                label
                if isinstance(label, str)
                else None
            ),
        )

    @staticmethod
    def _decimal_value(
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

    @staticmethod
    def _optional_string(
        value: object,
    ) -> str | None:
        if not isinstance(
            value,
            str,
        ):
            return None

        normalized = value.strip()

        return normalized or None