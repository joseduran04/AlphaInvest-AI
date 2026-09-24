from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.market.infrastructure.models import (
    HistoricalPriceModel,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.simulation.domain.exceptions import (
    SimulationHistoricalPriceNotFoundError,
    SimulationHistoricalSourceUnavailableError,
)
from alphainvest.modules.simulation.domain.historical import (
    HistoricalAssetInput,
    HistoricalPricePoint,
)


class HistoricalDataService:
    """Carga y normaliza históricos requeridos por Simulation."""

    def __init__(
        self,
        *,
        market_repository: MarketRepository,
        source_name: str,
        fallback_source_names: Sequence[str] = (),
    ) -> None:
        normalized_source_name = source_name.strip()

        if not normalized_source_name:
            raise ValueError(
                "El nombre de la fuente histórica "
                "no puede estar vacío"
            )

        self._market_repository = market_repository
        self._source_name = normalized_source_name
        self._source_names = [normalized_source_name] + [
            name.strip()
            for name in fallback_source_names
            if name.strip()
            and name.strip() != normalized_source_name
        ]

    async def load_asset_history(
        self,
        *,
        asset_id: UUID,
        assigned_percentage: Decimal,
        start_date: date,
        end_date: date,
    ) -> HistoricalAssetInput:
        # Se elige, entre las fuentes configuradas, la que tenga el
        # precio más reciente dentro del periodo. En empate gana la de
        # mayor prioridad. Así un activo que solo se sincronizó en una
        # fuente no recorta el periodo efectivo sin necesidad.
        available_sources = 0
        prices: Sequence[HistoricalPriceModel] = ()

        for name in self._source_names:
            source = (
                await self._market_repository
                .get_financial_source_by_name(
                    name=name,
                    active_only=True,
                )
            )

            if source is None:
                continue

            available_sources += 1

            candidate = (
                await self._market_repository
                .list_asset_prices_for_simulation(
                    asset_id=asset_id,
                    source_id=source.id,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

            if candidate and (
                not prices
                or candidate[-1].fecha > prices[-1].fecha
            ):
                prices = candidate

        if available_sources == 0:
            raise SimulationHistoricalSourceUnavailableError(
                "La fuente financiera histórica "
                f"'{self._source_name}' no está disponible"
            )

        if not prices:
            raise SimulationHistoricalPriceNotFoundError(
                "No existen precios históricos para "
                "el activo dentro del periodo solicitado"
            )

        normalized_prices = tuple(
            HistoricalPricePoint(
                date=price.fecha,
                price=(
                    price.cierre_ajustado
                    if price.cierre_ajustado is not None
                    else price.cierre
                ),
            )
            for price in prices
        )

        return HistoricalAssetInput(
            asset_id=asset_id,
            assigned_percentage=assigned_percentage,
            prices=normalized_prices,
        )