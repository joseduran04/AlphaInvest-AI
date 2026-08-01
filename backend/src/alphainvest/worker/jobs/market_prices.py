import logging

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.modules.market.application.synchronization_service import (
    PriceSynchronizationService,
)
from alphainvest.modules.market.domain.exceptions import (
    ProcessLockUnavailableError,
)
from alphainvest.modules.market.infrastructure.providers.factory import (
    create_alpha_vantage_provider,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

logger = logging.getLogger(__name__)


async def synchronize_configured_market_prices(
    settings: Settings,
) -> None:
    """Sincroniza los símbolos permitidos en la configuración."""

    symbols = settings.worker_price_symbols

    if not symbols:
        logger.warning(
            "El worker no tiene símbolos configurados"
        )
        return

    for symbol in symbols:
        async with AsyncSessionFactory() as session:
            market_repository = MarketRepository(session)
            operation_repository = OperationRepository(session)
            provider = create_alpha_vantage_provider(settings)

            asset = (
                await market_repository
                .get_active_asset_by_symbol(symbol)
            )

            if asset is None:
                logger.warning(
                    "No existe un activo activo para %s",
                    symbol,
                )
                continue

            service = PriceSynchronizationService(
                market_repository=market_repository,
                operation_repository=operation_repository,
                provider=provider,
            )

            try:
                result = await service.synchronize_asset(
                    asset_id=asset.id,
                    requested_by=None,
                )

                logger.info(
                    (
                        "Sincronización completada: "
                        "symbol=%s execution_id=%s "
                        "received=%s created=%s updated=%s"
                    ),
                    result.symbol,
                    result.execution_id,
                    result.received,
                    result.created,
                    result.updated,
                )

            except ProcessLockUnavailableError:
                logger.info(
                    "El activo %s ya está siendo procesado",
                    symbol,
                )

            except Exception:
                logger.exception(
                    "Falló la sincronización programada de %s",
                    symbol,
                )