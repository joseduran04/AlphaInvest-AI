import asyncio

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.market.infrastructure.providers.yahoo_finance import (
    YahooFinanceProvider,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"


async def bootstrap() -> None:
    provider = YahooFinanceProvider()

    async with AsyncSessionFactory() as session:
        repository = MarketRepository(session)

        asset = (
            await repository
            .get_active_asset_by_symbol(
                SYMBOL
            )
        )

        if asset is None:
            raise RuntimeError(
                f"No existe el activo {SYMBOL}"
            )

        source = (
            await repository
            .get_financial_source_by_name(
                name=provider.source_name,
                active_only=True,
            )
        )

        if source is None:
            raise RuntimeError(
                "No existe la fuente activa "
                "Yahoo Finance"
            )

        print("Descargando histórico...")
        print(f"Activo: {asset.simbolo}")
        print(f"Fuente: {source.nombre}")

        prices = await provider.fetch_daily_prices(
            symbol=asset.simbolo,
            currency=asset.moneda,
        )

        print(f"Recibidos: {len(prices)}")

        if not prices:
            raise RuntimeError(
                "Yahoo Finance no devolvió precios"
            )

        dates = [
            price.date
            for price in prices
        ]

        existing_dates = (
            await repository
            .get_existing_price_dates(
                asset_id=asset.id,
                source_id=source.id,
                dates=dates,
            )
        )

        created = sum(
            1
            for price_date in dates
            if price_date not in existing_dates
        )

        updated = (
            len(prices)
            - created
        )

        print(f"Nuevos:     {created}")
        print(f"Existentes: {updated}")
        print(
            f"Primera:    {prices[0].date}"
        )
        print(
            f"Última:     {prices[-1].date}"
        )

        try:
            await repository.upsert_daily_prices(
                asset_id=asset.id,
                source_id=source.id,
                prices=prices,
            )

            await repository.mark_source_requested(
                source
            )

            await repository.commit()

        except Exception:
            await repository.rollback()
            raise

        print()
        print("Bootstrap completado.")


async def main() -> None:
    try:
        await bootstrap()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())