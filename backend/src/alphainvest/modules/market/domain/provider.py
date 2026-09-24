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
        asset_type: str,
        market_code: str | None = None,
    ) -> list[DailyPricePoint]:
        """Obtiene y normaliza precios diarios.

        ``market_code`` permite traducir el símbolo a la convención
        del proveedor (por ejemplo, sufijo .MX para la BMV).
        """