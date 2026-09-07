from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from typing import Any

from bson import ObjectId
from bson.decimal128 import Decimal128
from pymongo import ASCENDING, DESCENDING

from alphainvest.infrastructure.mongodb.client import (
    MongoClientType,
)
from alphainvest.modules.news.domain.news_document import (
    NewsDocument,
    NewsTickerSentiment,
    NewsTopic,
)
from alphainvest.modules.news.domain.news_persistence import (
    NewsPersistenceResult,
)


class MongoNewsRepository:
    """Persistencia documental de noticias en MongoDB."""

    def __init__(
        self,
        *,
        client: MongoClientType,
        database_name: str,
        collection_name: str,
    ) -> None:
        self._collection = (
            client[database_name][collection_name]
        )

    async def ensure_indexes(self) -> None:
        """Crea los índices requeridos por el contrato documental."""

        await self._collection.create_index(
            [
                (
                    "deduplication_key",
                    ASCENDING,
                )
            ],
            unique=True,
            name="uq_news_deduplication_key",
        )

        await self._collection.create_index(
            [
                (
                    "published_at",
                    DESCENDING,
                )
            ],
            name="ix_news_published_at",
        )

        await self._collection.create_index(
            [
                (
                    "ticker_sentiment.ticker",
                    ASCENDING,
                ),
                (
                    "published_at",
                    DESCENDING,
                ),
            ],
            name=(
                "ix_news_ticker_published_at"
            ),
        )

    async def upsert_news(
        self,
        *,
        document: NewsDocument,
        provider_name: str,
    ) -> NewsPersistenceResult:
        normalized_provider = (
            provider_name.strip()
        )

        if not normalized_provider:
            raise ValueError(
                "El nombre del proveedor "
                "no puede estar vacío"
            )

        deduplication_key = (
            self.build_deduplication_key(
                provider_name=(
                    normalized_provider
                ),
                url=document.url,
            )
        )

        now = datetime.now(UTC)

        mongo_document = (
            self._serialize_document(
                document=document,
                provider_name=(
                    normalized_provider
                ),
                deduplication_key=(
                    deduplication_key
                ),
            )
        )

        result = await self._collection.update_one(
            {
                "deduplication_key": (
                    deduplication_key
                )
            },
            {
                "$set": {
                    **mongo_document,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "created_at": now,
                },
            },
            upsert=True,
        )

        created = (
            result.upserted_id
            is not None
        )

        if result.upserted_id is not None:
            document_id = (
                result.upserted_id
            )
        else:
            stored_document = (
                await self._collection.find_one(
                    {
                        "deduplication_key": (
                            deduplication_key
                        )
                    },
                    {
                        "_id": 1,
                    },
                )
            )

            if stored_document is None:
                raise RuntimeError(
                    "MongoDB no devolvió la "
                    "noticia persistida"
                )

            document_id = (
                stored_document.get("_id")
            )

        if not isinstance(
            document_id,
            ObjectId,
        ):
            raise RuntimeError(
                "MongoDB devolvió un "
                "identificador inválido"
            )

        return NewsPersistenceResult(
            document_id=str(document_id),
            created=created,
            deduplication_key=(
                deduplication_key
            ),
        )

    async def delete_by_document_id(
        self,
        document_id: str,
    ) -> bool:
        try:
            object_id = ObjectId(
                document_id
            )
        except Exception as error:
            raise ValueError(
                "El identificador MongoDB "
                "no es válido"
            ) from error

        result = (
            await self._collection.delete_one(
                {
                    "_id": object_id,
                }
            )
        )

        return result.deleted_count == 1

    async def get_by_document_id(
        self,
        document_id: str,
    ) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(
                document_id
            )
        except Exception as error:
            raise ValueError(
                "El identificador MongoDB "
                "no es válido"
            ) from error

        return await self._collection.find_one(
            {
                "_id": object_id,
            }
        )

    @staticmethod
    def build_deduplication_key(
        *,
        provider_name: str,
        url: str,
    ) -> str:
        normalized_provider = (
            provider_name
            .strip()
            .casefold()
        )

        normalized_url = (
            url.strip()
        )

        if not normalized_provider:
            raise ValueError(
                "El proveedor no puede "
                "estar vacío"
            )

        if not normalized_url:
            raise ValueError(
                "La URL no puede estar vacía"
            )

        raw_key = (
            f"{normalized_provider}|"
            f"{normalized_url}"
        )

        return sha256(
            raw_key.encode("utf-8")
        ).hexdigest()

    @classmethod
    def _serialize_document(
        cls,
        *,
        document: NewsDocument,
        provider_name: str,
        deduplication_key: str,
    ) -> dict[str, Any]:
        return {
            "provider": provider_name,
            "deduplication_key": (
                deduplication_key
            ),
            "title": document.title,
            "url": document.url,
            "published_at": (
                document.published_at
            ),
            "authors": list(
                document.authors
            ),
            "summary": document.summary,
            "banner_image": (
                document.banner_image
            ),
            "source": document.source,
            "category_within_source": (
                document
                .category_within_source
            ),
            "source_domain": (
                document.source_domain
            ),
            "topics": [
                cls._serialize_topic(
                    topic
                )
                for topic in document.topics
            ],
            "provider_sentiment": {
                "score": (
                    cls._to_decimal128(
                        document
                        .provider_sentiment_score
                    )
                ),
                "label": (
                    document
                    .provider_sentiment_label
                ),
            },
            "ticker_sentiment": [
                cls._serialize_ticker_sentiment(
                    item
                )
                for item in (
                    document
                    .ticker_sentiment
                )
            ],
            "raw_payload": (
                document.raw_payload
            ),
        }

    @staticmethod
    def _serialize_topic(
        topic: NewsTopic,
    ) -> dict[str, Any]:
        return {
            "topic": topic.topic,
            "relevance_score": (
                Decimal128(
                    topic.relevance_score
                )
            ),
        }

    @staticmethod
    def _serialize_ticker_sentiment(
        item: NewsTickerSentiment,
    ) -> dict[str, Any]:
        return {
            "ticker": item.ticker,
            "relevance_score": Decimal128(
                item.relevance_score
            ),
            "sentiment_score": Decimal128(
                item.sentiment_score
            ),
            "sentiment_label": (
                item.sentiment_label
            ),
        }

    @staticmethod
    def _to_decimal128(
        value: Decimal | None,
    ) -> Decimal128 | None:
        if value is None:
            return None

        return Decimal128(value)