from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.market.application.service import (
    MarketService,
)
from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    HistoricalPriceNotFoundError,
    InvalidPriceDateRangeError,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_markets_returns_items_and_total() -> None:
    market = SimpleNamespace(
        id=uuid4(),
        codigo="NASDAQ",
        nombre="NASDAQ",
        pais="Estados Unidos",
        zona_horaria="America/New_York",
        moneda="USD",
        activo=True,
    )

    repository = SimpleNamespace(
        list_markets=AsyncMock(
            return_value=[market]
        )
    )
    service = MarketService(repository)

    result = await service.list_markets(
        active_only=True
    )

    assert result.total == 1
    assert result.items[0].code == "NASDAQ"
    repository.list_markets.assert_awaited_once_with(
        active_only=True
    )


@pytest.mark.asyncio
async def test_list_asset_types_returns_items() -> None:
    asset_type = SimpleNamespace(
        id=uuid4(),
        codigo="ACCION",
        nombre="Acción",
        descripcion="Instrumento de renta variable",
        activo=True,
    )

    repository = SimpleNamespace(
        list_asset_types=AsyncMock(
            return_value=[asset_type]
        )
    )
    service = MarketService(repository)

    result = await service.list_asset_types(
        active_only=True
    )

    assert result.total == 1
    assert result.items[0].code == "ACCION"


@pytest.mark.asyncio
async def test_get_asset_raises_when_missing() -> None:
    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=None)
    )
    service = MarketService(repository)

    with pytest.raises(
        AssetNotFoundError,
        match="El activo solicitado no existe",
    ):
        await service.get_asset(
            asset_id=uuid4()
        )


@pytest.mark.asyncio
async def test_list_financial_sources_returns_items() -> None:
    source = SimpleNamespace(
        id=uuid4(),
        nombre="Alpha Vantage",
        proveedor="Alpha Vantage Inc.",
        url_base="https://www.alphavantage.co",
        prioridad=1,
        activa=True,
        requiere_api_key=True,
        limite_consultas_minuto=5,
        ultima_consulta=None,
    )

    repository = SimpleNamespace(
        list_financial_sources=AsyncMock(
            return_value=[source]
        )
    )
    service = MarketService(repository)

    result = await service.list_financial_sources(
        active_only=True
    )

    assert result.total == 1
    assert result.items[0].name == "Alpha Vantage"
    assert result.items[0].requires_api_key is True


@pytest.mark.asyncio
async def test_price_history_rejects_invalid_dates() -> None:
    repository = SimpleNamespace()
    service = MarketService(repository)

    with pytest.raises(
        InvalidPriceDateRangeError,
        match="fecha inicial",
    ):
        await service.get_asset_price_history(
            asset_id=uuid4(),
            start_date=date(2026, 7, 20),
            end_date=date(2026, 7, 10),
            source_id=None,
            limit=100,
            offset=0,
        )


@pytest.mark.asyncio
async def test_price_history_raises_when_asset_missing() -> None:
    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=None)
    )
    service = MarketService(repository)

    with pytest.raises(AssetNotFoundError):
        await service.get_asset_price_history(
            asset_id=uuid4(),
            start_date=None,
            end_date=None,
            source_id=None,
            limit=100,
            offset=0,
        )


@pytest.mark.asyncio
async def test_price_history_raises_when_source_missing() -> None:
    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(id=uuid4())
        ),
        get_financial_source=AsyncMock(
            return_value=None
        ),
    )
    service = MarketService(repository)

    with pytest.raises(FinancialSourceNotFoundError):
        await service.get_asset_price_history(
            asset_id=uuid4(),
            start_date=None,
            end_date=None,
            source_id=uuid4(),
            limit=100,
            offset=0,
        )


@pytest.mark.asyncio
async def test_price_history_returns_empty_list() -> None:
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(id=asset_id)
        ),
        list_asset_prices=AsyncMock(
            return_value=([], 0)
        ),
    )
    service = MarketService(repository)

    result = await service.get_asset_price_history(
        asset_id=asset_id,
        start_date=None,
        end_date=None,
        source_id=None,
        limit=100,
        offset=0,
    )

    assert result.asset_id == asset_id
    assert result.items == []
    assert result.total == 0


@pytest.mark.asyncio
async def test_latest_price_raises_when_price_missing() -> None:
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
            )
        ),
        get_latest_asset_price=AsyncMock(
            return_value=None
        ),
    )
    service = MarketService(repository)

    with pytest.raises(HistoricalPriceNotFoundError):
        await service.get_latest_asset_price(
            asset_id=asset_id,
            source_id=None,
        )


@pytest.mark.asyncio
async def test_latest_price_returns_price() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    source = SimpleNamespace(
        id=source_id,
        nombre="Carga Manual",
        proveedor="AlphaInvest AI",
    )

    price = SimpleNamespace(
        id=1,
        fecha=date(2026, 7, 28),
        apertura=Decimal("210.00"),
        maximo=Decimal("215.00"),
        minimo=Decimal("208.00"),
        cierre=Decimal("214.50"),
        cierre_ajustado=Decimal("214.50"),
        volumen=Decimal("1000000"),
        moneda="USD",
        fecha_registro=datetime.now(UTC),
        fuente=source,
    )

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
            )
        ),
        get_latest_asset_price=AsyncMock(
            return_value=price
        ),
    )
    service = MarketService(repository)

    result = await service.get_latest_asset_price(
        asset_id=asset_id,
        source_id=None,
    )

    assert result.asset_id == asset_id
    assert result.symbol == "AAPL"
    assert result.price.close == Decimal("214.50")