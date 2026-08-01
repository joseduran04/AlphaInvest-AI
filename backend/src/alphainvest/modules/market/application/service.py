from datetime import date
from uuid import UUID

from alphainvest.modules.market.domain.enums import (
    AssetStatus,
)
from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    HistoricalPriceNotFoundError,
    InvalidPriceDateRangeError,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.market.presentation.schemas import (
    AssetListResponse,
    AssetResponse,
    AssetTypeListResponse,
    AssetTypeResponse,
    FinancialSourceListResponse,
    FinancialSourceResponse,
    HistoricalPriceListResponse,
    HistoricalPriceResponse,
    LatestPriceResponse,
    MarketListResponse,
    MarketResponse,
)


class MarketService:
    """Casos de uso de consulta del mercado financiero."""

    def __init__(
        self,
        repository: MarketRepository,
    ) -> None:
        self._repository = repository

    async def list_markets(
        self,
        *,
        active_only: bool,
    ) -> MarketListResponse:
        markets = await self._repository.list_markets(
            active_only=active_only
        )

        items = [
            MarketResponse.model_validate(market)
            for market in markets
        ]

        return MarketListResponse(
            items=items,
            total=len(items),
        )

    async def list_asset_types(
        self,
        *,
        active_only: bool,
    ) -> AssetTypeListResponse:
        asset_types = (
            await self._repository.list_asset_types(
                active_only=active_only
            )
        )

        items = [
            AssetTypeResponse.model_validate(asset_type)
            for asset_type in asset_types
        ]

        return AssetTypeListResponse(
            items=items,
            total=len(items),
        )

    async def list_assets(
        self,
        *,
        search: str | None,
        market_code: str | None,
        asset_type_code: str | None,
        sector: str | None,
        currency: str | None,
        status: AssetStatus | None,
        limit: int,
        offset: int,
    ) -> AssetListResponse:
        assets, total = await self._repository.list_assets(
            search=search,
            market_code=market_code,
            asset_type_code=asset_type_code,
            sector=sector,
            currency=currency,
            status=status.value if status else None,
            limit=limit,
            offset=offset,
        )

        return AssetListResponse(
            items=[
                AssetResponse.model_validate(asset)
                for asset in assets
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_asset(
        self,
        *,
        asset_id: UUID,
    ) -> AssetResponse:
        asset = await self._repository.get_asset(
            asset_id
        )

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        return AssetResponse.model_validate(asset)

    async def list_financial_sources(
        self,
        *,
        active_only: bool,
    ) -> FinancialSourceListResponse:
        sources = (
            await self._repository.list_financial_sources(
                active_only=active_only
            )
        )

        items = [
            FinancialSourceResponse.model_validate(source)
            for source in sources
        ]

        return FinancialSourceListResponse(
            items=items,
            total=len(items),
        )

    async def get_asset_price_history(
        self,
        *,
        asset_id: UUID,
        start_date: date | None,
        end_date: date | None,
        source_id: UUID | None,
        limit: int,
        offset: int,
    ) -> HistoricalPriceListResponse:
        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise InvalidPriceDateRangeError(
                "La fecha inicial no puede ser posterior "
                "a la fecha final"
            )

        asset = await self._repository.get_asset(asset_id)

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        if source_id is not None:
            source = (
                await self._repository.get_financial_source(
                    source_id
                )
            )

            if source is None:
                raise FinancialSourceNotFoundError(
                    "La fuente financiera solicitada "
                    "no existe"
                )

        prices, total = (
            await self._repository.list_asset_prices(
                asset_id=asset_id,
                start_date=start_date,
                end_date=end_date,
                source_id=source_id,
                limit=limit,
                offset=offset,
            )
        )

        return HistoricalPriceListResponse(
            asset_id=asset_id,
            items=[
                HistoricalPriceResponse.model_validate(price)
                for price in prices
            ],
            total=total,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_latest_asset_price(
        self,
        *,
        asset_id: UUID,
        source_id: UUID | None,
    ) -> LatestPriceResponse:
        asset = await self._repository.get_asset(asset_id)

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        if source_id is not None:
            source = (
                await self._repository.get_financial_source(
                    source_id
                )
            )

            if source is None:
                raise FinancialSourceNotFoundError(
                    "La fuente financiera solicitada "
                    "no existe"
                )

        price = await self._repository.get_latest_asset_price(
            asset_id=asset_id,
            source_id=source_id,
        )

        if price is None:
            raise HistoricalPriceNotFoundError(
                "No existen precios históricos "
                "para el activo solicitado"
            )

        return LatestPriceResponse(
            asset_id=asset.id,
            symbol=asset.simbolo,
            price=HistoricalPriceResponse.model_validate(
                price
            ),
        )