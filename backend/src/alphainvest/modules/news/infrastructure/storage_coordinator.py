from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.application.storage_service import (
    NewsStorageService,
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


class SqlAlchemyNewsStorageCoordinator:
    """Aísla la transacción SQL de cada persistencia de noticia."""

    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[
            AsyncSession
        ],
        mongo_repository: MongoNewsRepository,
    ) -> None:
        self._session_factory = session_factory
        self._mongo_repository = mongo_repository

    async def store_for_asset(
        self,
        *,
        asset_id: UUID,
        document: NewsDocument,
        provider_name: str,
        language: str | None = None,
    ) -> NewsStorageResult:
        async with self._session_factory() as session:
            market_repository = MarketRepository(
                session
            )

            service = NewsStorageService(
                market_repository=(
                    market_repository
                ),
                mongo_repository=(
                    self._mongo_repository
                ),
            )

            return await service.store_for_asset(
                asset_id=asset_id,
                document=document,
                provider_name=provider_name,
                language=language,
            )