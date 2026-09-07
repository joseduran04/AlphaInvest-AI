import logging

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.infrastructure.mongodb.client import (
    create_mongo_client,
)
from alphainvest.modules.market.domain.exceptions import (
    ProcessLockUnavailableError,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.application.synchronization_service import (
    NewsSynchronizationService,
)
from alphainvest.modules.news.infrastructure.mongodb_repository import (
    MongoNewsRepository,
)
from alphainvest.modules.news.infrastructure.providers.factory import (
    create_alpha_vantage_news_provider,
)
from alphainvest.modules.news.infrastructure.storage_coordinator import (
    SqlAlchemyNewsStorageCoordinator,
)
from alphainvest.modules.operation.domain.enums import (
    JobTrigger,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

logger = logging.getLogger(__name__)

NEWS_WORKER_LIMIT = 20


async def synchronize_configured_news(
    settings: Settings,
) -> None:
    """Sincroniza noticias para los símbolos habilitados."""

    symbols = settings.worker_price_symbols

    if not symbols:
        logger.warning(
            "El worker no tiene símbolos configurados "
            "para sincronizar noticias"
        )
        return

    mongo_client = create_mongo_client(
        settings
    )

    try:
        mongo_repository = (
            MongoNewsRepository(
                client=mongo_client,
                database_name=(
                    settings.mongodb_database
                ),
                collection_name=(
                    settings.mongodb_news_collection
                ),
            )
        )

        await mongo_repository.ensure_indexes()

        storage = (
            SqlAlchemyNewsStorageCoordinator(
                session_factory=(
                    AsyncSessionFactory
                ),
                mongo_repository=(
                    mongo_repository
                ),
            )
        )

        provider = (
            create_alpha_vantage_news_provider(
                settings
            )
        )

        for symbol in symbols:
            async with (
                AsyncSessionFactory()
                as session
            ):
                market_repository = (
                    MarketRepository(
                        session
                    )
                )

                operation_repository = (
                    OperationRepository(
                        session
                    )
                )

                asset = (
                    await market_repository
                    .get_active_asset_by_symbol(
                        symbol
                    )
                )

                if asset is None:
                    logger.warning(
                        (
                            "No existe un activo "
                            "activo para %s"
                        ),
                        symbol,
                    )
                    continue

                service = (
                    NewsSynchronizationService(
                        market_repository=(
                            market_repository
                        ),
                        operation_repository=(
                            operation_repository
                        ),
                        provider=provider,
                        storage=storage,
                    )
                )

                try:
                    result = (
                        await service
                        .synchronize_asset(
                            asset_id=asset.id,
                            requested_by=None,
                            start_at=None,
                            end_at=None,
                            limit=(
                                NEWS_WORKER_LIMIT
                            ),
                            trigger=(
                                JobTrigger.SCHEDULED
                            ),
                        )
                    )

                    logger.info(
                        (
                            "Noticias sincronizadas: "
                            "symbol=%s "
                            "execution_id=%s "
                            "received=%s "
                            "created=%s "
                            "reused=%s "
                            "failed=%s"
                        ),
                        result.symbol,
                        result.execution_id,
                        result.received,
                        result.created,
                        result.reused,
                        result.failed,
                    )

                except ProcessLockUnavailableError:
                    logger.info(
                        (
                            "Las noticias de %s "
                            "ya están siendo "
                            "sincronizadas"
                        ),
                        symbol,
                    )

                except Exception:
                    logger.exception(
                        (
                            "Falló la sincronización "
                            "programada de noticias "
                            "para %s"
                        ),
                        symbol,
                    )

                    raise

    finally:
        await mongo_client.close()