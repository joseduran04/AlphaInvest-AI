from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    PriceSynchronizationError,
)
from alphainvest.modules.market.domain.provider import (
    MarketDataProvider,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.market.presentation.schemas import (
    PriceSynchronizationResponse,
)


class PriceSynchronizationService:
    """Sincroniza precios externos con PostgreSQL."""

    def __init__(
        self,
        *,
        repository: MarketRepository,
        provider: MarketDataProvider,
    ) -> None:
        self._repository = repository
        self._provider = provider

    async def synchronize_asset(
        self,
        *,
        asset_id: UUID,
    ) -> PriceSynchronizationResponse:
        asset = await self._repository.get_asset(asset_id)

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        source = (
            await self._repository.get_financial_source_by_name(
                name=self._provider.source_name,
                active_only=True,
            )
        )

        if source is None:
            raise FinancialSourceNotFoundError(
                "No existe una fuente financiera activa "
                f"llamada {self._provider.source_name}"
            )

        prices = await self._provider.fetch_daily_prices(
            symbol=asset.simbolo,
            currency=asset.moneda,
        )

        price_dates = [
            price.date
            for price in prices
        ]

        existing_dates = (
            await self._repository.get_existing_price_dates(
                asset_id=asset.id,
                source_id=source.id,
                dates=price_dates,
            )
        )

        created = sum(
            1
            for price_date in price_dates
            if price_date not in existing_dates
        )
        updated = len(price_dates) - created

        try:
            await self._repository.upsert_daily_prices(
                asset_id=asset.id,
                source_id=source.id,
                prices=prices,
            )

            synchronized_at = (
                await self._repository.mark_source_requested(
                    source
                )
            )

            await self._repository.commit()

        except SQLAlchemyError as error:
            await self._repository.rollback()

            raise PriceSynchronizationError(
                "No fue posible guardar los precios "
                "sincronizados"
            ) from error

        return PriceSynchronizationResponse(
            asset_id=asset.id,
            symbol=asset.simbolo,
            source_id=source.id,
            source_name=source.nombre,
            received=len(prices),
            created=created,
            updated=updated,
            synchronized_at=synchronized_at,
            first_date=prices[0].date if prices else None,
            last_date=prices[-1].date if prices else None,
        )