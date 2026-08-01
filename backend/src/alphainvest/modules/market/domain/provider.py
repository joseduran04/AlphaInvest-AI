from typing import Protocol

from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)


class MarketDataProvider(Protocol):
    """Contrato independiente para proveedores financieros."""

    @property
    def source_name(self) -> str:
        """Nombre que debe coincidir con fuentes_financieras."""

    async def fetch_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
    ) -> list[DailyPricePoint]:
        """Obtiene y normaliza precios diarios."""