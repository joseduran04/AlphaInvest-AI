from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.portfolio.application.service import (
    PortfolioService,
)
from alphainvest.modules.portfolio.domain.exceptions import (
    PortfolioAssetNotFoundError,
    PortfolioAssetUnavailableError,
    PortfolioNameAlreadyExistsError,
    PortfolioNotFoundError,
    PortfolioUnavailableError,
    PositionAlreadyExistsError,
    PositionNotFoundError,
)
from alphainvest.modules.portfolio.presentation.schemas import (
    PortfolioCreateRequest,
    PortfolioValuationCreateRequest,
    PositionCreateRequest,
    PositionUpdateRequest,
)

pytestmark = pytest.mark.unit


def build_portfolio():
    return SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        nombre="Portafolio principal",
        descripcion=None,
        moneda_base="USD",
        capital_inicial=Decimal("10000"),
        saldo_efectivo=Decimal("10000"),
        tipo="VIRTUAL",
        estado="ACTIVO",
        fecha_inicio=date(2026, 8, 1),
        fecha_cierre=None,
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now(),
        posiciones=[],
    )


def build_asset():
    return SimpleNamespace(
        id=uuid4(),
        simbolo="ORCL",
        nombre="Oracle Corporation",
        moneda="USD",
        estado="ACTIVO",
    )


def build_position(
    *,
    portfolio_id=None,
    asset_id=None,
):
    now = datetime.now()

    return SimpleNamespace(
        id=uuid4(),
        portafolio_id=(
            portfolio_id or uuid4()
        ),
        activo_id=asset_id or uuid4(),
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal(
            "100"
        ),
        costo_total=Decimal("1000"),
        precio_actual=Decimal("110"),
        valor_actual=Decimal("1100"),
        ganancia_perdida=Decimal("100"),
        rendimiento_porcentaje=Decimal(
            "10"
        ),
        moneda="USD",
        estado="ABIERTA",
        fecha_apertura=now,
        fecha_actualizacion=now,
        fecha_cierre=None,
    )


def build_summary_data(
    *,
    initial_capital: Decimal = Decimal("10000"),
    estimated_total: Decimal = Decimal("10600"),
):
    now = datetime.now()

    return {
        "portafolio_id": uuid4(),
        "usuario_id": uuid4(),
        "portafolio_nombre": "Portafolio principal",
        "descripcion": None,
        "moneda_base": "USD",
        "capital_inicial": initial_capital,
        "saldo_efectivo": Decimal("2500"),
        "tipo": "VIRTUAL",
        "estado": "ACTIVO",
        "fecha_inicio": date(2026, 8, 1),
        "fecha_cierre": None,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
        "posiciones_abiertas": 2,
        "posiciones_totales": 2,
        "capital_invertido": Decimal("7500"),
        "valor_posiciones": Decimal("8100"),
        "valor_total_estimado": estimated_total,
        "ganancia_perdida_posiciones": Decimal(
            "600"
        ),
    }


@pytest.mark.asyncio
async def test_create_rejects_duplicate_name() -> None:
    repository = SimpleNamespace(
        get_by_name_for_user=AsyncMock(
            return_value=build_portfolio()
        )
    )

    service = PortfolioService(repository)

    request = PortfolioCreateRequest(
        nombre="Portafolio principal",
        capital_inicial=Decimal("10000"),
    )

    with pytest.raises(
        PortfolioNameAlreadyExistsError
    ):
        await service.create_portfolio(
            user_id=uuid4(),
            request=request,
        )


@pytest.mark.asyncio
async def test_create_portfolio() -> None:
    portfolio = build_portfolio()

    repository = SimpleNamespace(
        get_by_name_for_user=AsyncMock(
            return_value=None
        ),
        create=AsyncMock(
            return_value=portfolio
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = PortfolioService(repository)

    request = PortfolioCreateRequest(
        nombre="Portafolio principal",
        capital_inicial=Decimal("10000"),
    )

    response = await service.create_portfolio(
        user_id=portfolio.usuario_id,
        request=request,
    )

    assert response.nombre == "Portafolio principal"
    assert response.saldo_efectivo == Decimal(
        "10000"
    )

    repository.create.assert_awaited_once()
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_close_rejects_open_positions() -> None:
    portfolio = build_portfolio()
    portfolio.posiciones = [
        SimpleNamespace(
            estado="ABIERTA",
            cantidad=Decimal("2"),
        )
    ]

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        )
    )

    service = PortfolioService(repository)

    with pytest.raises(
        PortfolioUnavailableError,
        match="posiciones abiertas",
    ):
        await service.close_portfolio(
            portfolio_id=portfolio.id,
            user_id=portfolio.usuario_id,
        )


@pytest.mark.asyncio
async def test_create_position_rejects_missing_asset(
) -> None:
    portfolio = build_portfolio()

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        )
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=None
        )
    )

    service = PortfolioService(
        repository,
        market_repository,
    )

    request = PositionCreateRequest(
        activo_id=uuid4(),
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal(
            "100"
        ),
    )

    with pytest.raises(
        PortfolioAssetNotFoundError
    ):
        await service.create_position(
            portfolio_id=portfolio.id,
            user_id=portfolio.usuario_id,
            request=request,
        )


@pytest.mark.asyncio
async def test_create_position_rejects_inactive_asset(
) -> None:
    portfolio = build_portfolio()
    asset = build_asset()
    asset.estado = "INACTIVO"

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        )
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    service = PortfolioService(
        repository,
        market_repository,
    )

    request = PositionCreateRequest(
        activo_id=asset.id,
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal(
            "100"
        ),
    )

    with pytest.raises(
        PortfolioAssetUnavailableError
    ):
        await service.create_position(
            portfolio_id=portfolio.id,
            user_id=portfolio.usuario_id,
            request=request,
        )


@pytest.mark.asyncio
async def test_create_position_rejects_duplicate(
) -> None:
    portfolio = build_portfolio()
    asset = build_asset()
    existing = build_position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
    )

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        get_position_by_asset=AsyncMock(
            return_value=existing
        ),
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    service = PortfolioService(
        repository,
        market_repository,
    )

    request = PositionCreateRequest(
        activo_id=asset.id,
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal(
            "100"
        ),
    )

    with pytest.raises(
        PositionAlreadyExistsError
    ):
        await service.create_position(
            portfolio_id=portfolio.id,
            user_id=portfolio.usuario_id,
            request=request,
        )


@pytest.mark.asyncio
async def test_create_position_without_market_price(
) -> None:
    portfolio = build_portfolio()
    asset = build_asset()
    position = build_position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
    )
    position.precio_actual = None
    position.valor_actual = None
    position.ganancia_perdida = None
    position.rendimiento_porcentaje = None

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        get_position_by_asset=AsyncMock(
            return_value=None
        ),
        create_position=AsyncMock(
            return_value=position
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        ),
        get_latest_asset_price=AsyncMock(
            return_value=None
        ),
    )

    service = PortfolioService(
        repository,
        market_repository,
    )

    request = PositionCreateRequest(
        activo_id=asset.id,
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal(
            "100"
        ),
    )

    response = await service.create_position(
        portfolio_id=portfolio.id,
        user_id=portfolio.usuario_id,
        request=request,
    )

    assert response.activo_id == asset.id
    assert response.precio_actual is None

    repository.create_position.assert_awaited_once_with(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("10"),
        average_purchase_price=Decimal(
            "100"
        ),
        currency="USD",
        current_price=None,
        opening_date=None,
    )
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_position_rejects_missing_position(
) -> None:
    portfolio = build_portfolio()

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        get_position_by_id=AsyncMock(
            return_value=None
        ),
    )
    market_repository = SimpleNamespace()

    service = PortfolioService(
        repository,
        market_repository,
    )

    request = PositionUpdateRequest(
        cantidad=Decimal("15")
    )

    with pytest.raises(PositionNotFoundError):
        await service.update_position(
            portfolio_id=portfolio.id,
            position_id=uuid4(),
            user_id=portfolio.usuario_id,
            request=request,
        )


@pytest.mark.asyncio
async def test_delete_position() -> None:
    portfolio = build_portfolio()
    position = build_position(
        portfolio_id=portfolio.id
    )

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        get_position_by_id=AsyncMock(
            return_value=position
        ),
        delete_position=AsyncMock(),
        commit=AsyncMock(),
    )

    service = PortfolioService(
        repository,
        SimpleNamespace(),
    )

    await service.delete_position(
        portfolio_id=portfolio.id,
        position_id=position.id,
        user_id=portfolio.usuario_id,
    )

    repository.delete_position.assert_awaited_once_with(
        position
    )
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_summary_rejects_missing_portfolio(
) -> None:
    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=None
        )
    )

    service = PortfolioService(repository)

    with pytest.raises(PortfolioNotFoundError):
        await service.get_portfolio_summary(
            portfolio_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_summary_without_latest_valuation(
) -> None:
    summary_data = build_summary_data()

    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=summary_data
        ),
        get_latest_valuation=AsyncMock(
            return_value=None
        ),
    )

    service = PortfolioService(repository)

    response = await service.get_portfolio_summary(
        portfolio_id=summary_data[
            "portafolio_id"
        ],
        user_id=summary_data["usuario_id"],
    )

    assert (
        response.resumen.ganancia_perdida_total
        == Decimal("600")
    )
    assert (
        response.resumen
        .rendimiento_estimado_porcentaje
        == Decimal("6")
    )
    assert response.ultima_valoracion is None


@pytest.mark.asyncio
async def test_get_summary_with_zero_initial_capital(
) -> None:
    summary_data = build_summary_data(
        initial_capital=Decimal("0"),
        estimated_total=Decimal("0"),
    )

    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=summary_data
        ),
        get_latest_valuation=AsyncMock(
            return_value=None
        ),
    )

    service = PortfolioService(repository)

    response = await service.get_portfolio_summary(
        portfolio_id=summary_data[
            "portafolio_id"
        ],
        user_id=summary_data["usuario_id"],
    )

    assert (
        response.resumen
        .rendimiento_estimado_porcentaje
        is None
    )


@pytest.mark.asyncio
async def test_get_summary_with_latest_valuation(
) -> None:
    summary_data = build_summary_data()
    now = datetime.now()

    valuation_data = {
        "portafolio_id": summary_data[
            "portafolio_id"
        ],
        "fecha_hora": now,
        "saldo_efectivo": Decimal("2500"),
        "valor_posiciones": Decimal("8100"),
        "valor_total": Decimal("10600"),
        "capital_invertido": Decimal("7500"),
        "ganancia_perdida": Decimal("600"),
        "rendimiento_porcentaje": Decimal("6"),
        "moneda": "USD",
        "fecha_registro": now,
    }

    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=summary_data
        ),
        get_latest_valuation=AsyncMock(
            return_value=valuation_data
        ),
    )

    service = PortfolioService(repository)

    response = await service.get_portfolio_summary(
        portfolio_id=summary_data[
            "portafolio_id"
        ],
        user_id=summary_data["usuario_id"],
    )

    assert response.ultima_valoracion is not None
    assert (
        response.ultima_valoracion.valor_total
        == Decimal("10600")
    )


@pytest.mark.asyncio
async def test_get_asset_allocation() -> None:
    summary_data = build_summary_data()
    portfolio_id = summary_data["portafolio_id"]
    user_id = summary_data["usuario_id"]
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=summary_data
        ),
        get_asset_allocation=AsyncMock(
            return_value=[
                {
                    "activo_id": asset_id,
                    "simbolo": "ORCL",
                    "nombre": "Oracle Corporation",
                    "sector": "Technology",
                    "industria": "Software",
                    "cantidad": Decimal("10"),
                    "valor_referencia": Decimal(
                        "1500"
                    ),
                    "porcentaje": Decimal("100"),
                }
            ]
        ),
    )

    service = PortfolioService(repository)

    response = await service.get_asset_allocation(
        portfolio_id=portfolio_id,
        user_id=user_id,
    )

    assert response.portafolio_id == portfolio_id
    assert (
        response.valor_total_distribuido
        == Decimal("1500")
    )
    assert response.items[0].simbolo == "ORCL"
    assert (
        response.items[0].porcentaje
        == Decimal("100")
    )


@pytest.mark.asyncio
async def test_get_sector_allocation() -> None:
    summary_data = build_summary_data()
    portfolio_id = summary_data["portafolio_id"]
    user_id = summary_data["usuario_id"]

    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=summary_data
        ),
        get_sector_allocation=AsyncMock(
            return_value=[
                {
                    "sector": "Technology",
                    "posiciones": 2,
                    "valor_referencia": Decimal(
                        "2000"
                    ),
                    "porcentaje": Decimal("100"),
                }
            ]
        ),
    )

    service = PortfolioService(repository)

    response = await service.get_sector_allocation(
        portfolio_id=portfolio_id,
        user_id=user_id,
    )

    assert (
        response.valor_total_distribuido
        == Decimal("2000")
    )
    assert response.items[0].sector == "Technology"
    assert response.items[0].posiciones == 2


@pytest.mark.asyncio
async def test_allocation_rejects_missing_portfolio(
) -> None:
    repository = SimpleNamespace(
        get_portfolio_summary=AsyncMock(
            return_value=None
        )
    )

    service = PortfolioService(repository)

    with pytest.raises(PortfolioNotFoundError):
        await service.get_asset_allocation(
            portfolio_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_register_portfolio_valuation(
) -> None:
    portfolio = build_portfolio()
    now = datetime.now()

    valuation = SimpleNamespace(
        id=42,
        portafolio_id=portfolio.id,
        fecha_hora=now,
        saldo_efectivo=Decimal("2500"),
        valor_posiciones=Decimal("8100"),
        valor_total=Decimal("10600"),
        capital_invertido=Decimal("10000"),
        ganancia_perdida=Decimal("600"),
        rendimiento_porcentaje=Decimal("6"),
        moneda="USD",
        detalle={
            "origen": "API_MANUAL",
            "posiciones_abiertas": 2,
        },
        fecha_registro=now,
    )

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        register_valuation=AsyncMock(
            return_value=42
        ),
        get_valuation_by_id=AsyncMock(
            return_value=valuation
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = PortfolioService(repository)

    request = PortfolioValuationCreateRequest(
        detalle={
            "origen": "API_MANUAL",
        }
    )

    response = (
        await service.register_portfolio_valuation(
            portfolio_id=portfolio.id,
            user_id=portfolio.usuario_id,
            request=request,
        )
    )

    assert response.id == 42
    assert response.valor_total == Decimal(
        "10600"
    )
    assert (
        response.rendimiento_porcentaje
        == Decimal("6")
    )

    repository.register_valuation.assert_awaited_once_with(
        portfolio_id=portfolio.id,
        valuation_date=None,
        details={
            "origen": "API_MANUAL",
        },
    )
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_valuation_rejects_missing_portfolio(
) -> None:
    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=None
        )
    )

    service = PortfolioService(repository)

    with pytest.raises(PortfolioNotFoundError):
        await service.register_portfolio_valuation(
            portfolio_id=uuid4(),
            user_id=uuid4(),
            request=PortfolioValuationCreateRequest(),
        )


@pytest.mark.asyncio
async def test_list_portfolio_valuations(
) -> None:
    portfolio = build_portfolio()
    now = datetime.now()

    valuation = SimpleNamespace(
        id=42,
        portafolio_id=portfolio.id,
        fecha_hora=now,
        saldo_efectivo=Decimal("2500"),
        valor_posiciones=Decimal("8100"),
        valor_total=Decimal("10600"),
        capital_invertido=Decimal("10000"),
        ganancia_perdida=Decimal("600"),
        rendimiento_porcentaje=Decimal("6"),
        moneda="USD",
        detalle=None,
        fecha_registro=now,
    )

    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        list_valuations=AsyncMock(
            return_value=([valuation], 1)
        ),
    )

    service = PortfolioService(repository)

    response = (
        await service.list_portfolio_valuations(
            portfolio_id=portfolio.id,
            user_id=portfolio.usuario_id,
            limit=50,
            offset=0,
        )
    )

    assert response.total == 1
    assert response.limit == 50
    assert response.offset == 0
    assert response.items[0].id == 42


@pytest.mark.asyncio
async def test_list_valuations_rejects_missing_portfolio(
) -> None:
    repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=None
        )
    )

    service = PortfolioService(repository)

    with pytest.raises(PortfolioNotFoundError):
        await service.list_portfolio_valuations(
            portfolio_id=uuid4(),
            user_id=uuid4(),
            limit=50,
            offset=0,
        )