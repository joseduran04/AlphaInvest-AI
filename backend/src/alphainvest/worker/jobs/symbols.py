import logging

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

logger = logging.getLogger(__name__)


def merge_symbols(
    configured: list[str],
    in_use: list[str],
) -> list[str]:
    """Une símbolos configurados y en uso sin duplicados, en orden estable."""

    merged: list[str] = []

    for symbol in [*configured, *in_use]:
        normalized = symbol.strip().upper()

        if normalized and normalized not in merged:
            merged.append(normalized)

    return merged


async def resolve_worker_symbols(
    settings: Settings,
) -> list[str]:
    """Símbolos que el worker debe sincronizar (precios y noticias)."""

    configured = settings.worker_price_symbols
    sync_all = getattr(
        settings,
        "worker_sync_all_active_assets",
        False,
    ) is True
    sync_in_use = getattr(
        settings,
        "worker_price_sync_assets_in_use",
        False,
    ) is True

    if not sync_all and not sync_in_use:
        return configured

    try:
        async with AsyncSessionFactory() as session:
            repository = MarketRepository(session)
            extra = (
                await repository.list_active_symbols()
                if sync_all
                else await repository.list_symbols_in_use()
            )
    except Exception:
        logger.exception(
            "No fue posible consultar los activos a sincronizar; "
            "se usará solo la lista configurada"
        )
        return configured

    return merge_symbols(configured, extra)
