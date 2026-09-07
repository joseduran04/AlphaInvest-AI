from decimal import Decimal
from uuid import UUID

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.domain.exceptions import (
    NewsPersistenceError,
)
from alphainvest.modules.news.domain.news_document import (
    NewsDocument,
)
from alphainvest.modules.news.domain.news_storage import (
    NewsStorageResult,
)
from alphainvest.modules.news.infrastructure.mongodb_repository import (
    MongoNewsRepository,
)


class NewsStorageService:
    """Coordina MongoDB con la referencia relacional Market."""

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

    async def store_for_asset(
        self,
        *,
        asset_id: UUID,
        document: NewsDocument,
        provider_name: str,
        language: str | None = None,
    ) -> NewsStorageResult:
        asset = (
            await self._market_repository
            .get_asset(asset_id)
        )

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        relevance = self._resolve_relevance(
            document=document,
            symbol=asset.simbolo,
        )

        mongo_result = (
            await self._mongo_repository
            .upsert_news(
                document=document,
                provider_name=provider_name,
            )
        )

        try:
            reference_id = (
                await self._market_repository
                .upsert_news_reference(
                    asset_id=asset_id,
                    mongo_document_id=(
                        mongo_result.document_id
                    ),
                    title=document.title,
                    source=document.source,
                    url=document.url,
                    published_at=(
                        document.published_at
                    ),
                    language=language,
                    relevance=relevance,
                )
            )

            await (
                self._market_repository
                .commit()
            )

        except Exception as error:
            await (
                self._market_repository
                .rollback()
            )

            if mongo_result.created:
                try:
                    await (
                        self._mongo_repository
                        .delete_by_document_id(
                            mongo_result
                            .document_id
                        )
                    )
                except Exception as compensation_error:
                    raise NewsPersistenceError(
                        "Falló PostgreSQL y también "
                        "la compensación del documento "
                        "MongoDB"
                    ) from compensation_error

            raise NewsPersistenceError(
                "No fue posible persistir "
                "la referencia PostgreSQL "
                "de la noticia"
            ) from error

        return NewsStorageResult(
            reference_id=reference_id,
            mongo_document_id=(
                mongo_result.document_id
            ),
            mongo_created=(
                mongo_result.created
            ),
        )

    @staticmethod
    def _resolve_relevance(
        *,
        document: NewsDocument,
        symbol: str,
    ) -> Decimal | None:
        normalized_symbol = (
            symbol.strip().upper()
        )

        for item in (
            document.ticker_sentiment
        ):
            if (
                item.ticker.strip().upper()
                == normalized_symbol
            ):
                return item.relevance_score

        return None