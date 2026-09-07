from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)

pytestmark = pytest.mark.unit


def build_session() -> MagicMock:
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    return session


@pytest.mark.asyncio
async def test_create_position() -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    portfolio_id = uuid4()
    asset_id = uuid4()
    opening_date = datetime(
        2026,
        8,
        1,
        15,
        30,
        tzinfo=UTC,
    )

    position = await repository.create_position(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        quantity=Decimal("10"),
        average_purchase_price=Decimal(
            "125.50"
        ),
        currency="USD",
        current_price=Decimal("130.00"),
        opening_date=opening_date,
    )

    assert position.portafolio_id == portfolio_id
    assert position.activo_id == asset_id
    assert position.cantidad == Decimal("10")
    assert (
        position.precio_promedio_compra
        == Decimal("125.50")
    )
    assert position.moneda == "USD"
    assert position.precio_actual == Decimal(
        "130.00"
    )
    assert position.fecha_apertura == opening_date

    session.add.assert_called_once_with(position)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        position
    )


@pytest.mark.asyncio
async def test_update_position() -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    original_date = datetime(
        2026,
        8,
        1,
        tzinfo=UTC,
    )
    updated_date = datetime(
        2026,
        8,
        2,
        tzinfo=UTC,
    )

    position = SimpleNamespace(
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal("100"),
        precio_actual=Decimal("105"),
        fecha_apertura=original_date,
    )

    updated = await repository.update_position(
        position,
        quantity=Decimal("15"),
        average_purchase_price=Decimal(
            "110"
        ),
        opening_date=updated_date,
        opening_date_was_sent=True,
        current_price=Decimal("115"),
    )

    assert updated.cantidad == Decimal("15")
    assert (
        updated.precio_promedio_compra
        == Decimal("110")
    )
    assert updated.precio_actual == Decimal(
        "115"
    )
    assert (
        updated.fecha_apertura
        == updated_date
    )

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        position
    )


@pytest.mark.asyncio
async def test_update_position_preserves_unsent_fields(
) -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    original_date = datetime(
        2026,
        8,
        1,
        tzinfo=UTC,
    )

    position = SimpleNamespace(
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal("100"),
        precio_actual=Decimal("105"),
        fecha_apertura=original_date,
    )

    updated = await repository.update_position(
        position,
        quantity=None,
        average_purchase_price=None,
        opening_date=None,
        opening_date_was_sent=False,
        current_price=Decimal("115"),
    )

    assert updated.cantidad == Decimal("10")
    assert (
        updated.precio_promedio_compra
        == Decimal("100")
    )
    assert updated.fecha_apertura == original_date
    assert updated.precio_actual == Decimal(
        "115"
    )


@pytest.mark.asyncio
async def test_update_position_rejects_null_opening_date(
) -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    position = SimpleNamespace(
        cantidad=Decimal("10"),
        precio_promedio_compra=Decimal("100"),
        precio_actual=None,
        fecha_apertura=datetime.now(UTC),
    )

    with pytest.raises(
        ValueError,
        match="fecha de apertura",
    ):
        await repository.update_position(
            position,
            quantity=None,
            average_purchase_price=None,
            opening_date=None,
            opening_date_was_sent=True,
            current_price=None,
        )

    session.flush.assert_not_awaited()
    session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_position() -> None:
    session = build_session()
    repository = PortfolioRepository(session)
    position = SimpleNamespace(id=uuid4())

    await repository.delete_position(position)

    session.delete.assert_awaited_once_with(
        position
    )
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_commit() -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    await repository.commit()

    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_rollback() -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    await repository.rollback()

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_valuation() -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one.return_value = 42
    session.execute.return_value = result

    repository = PortfolioRepository(session)
    portfolio_id = uuid4()

    valuation_id = await repository.register_valuation(
        portfolio_id=portfolio_id,
        valuation_date=None,
        details={
            "origen": "API_MANUAL",
        },
    )

    assert valuation_id == 42
    session.execute.assert_awaited_once()

    execute_call = session.execute.await_args
    parameters = execute_call.args[1]

    assert parameters["portfolio_id"] == portfolio_id
    assert parameters["valuation_date"] is None
    assert parameters["details"] == (
        '{"origen": "API_MANUAL"}'
    )


@pytest.mark.asyncio
async def test_list_valuations() -> None:
    session = build_session()
    repository = PortfolioRepository(session)

    valuation = SimpleNamespace(
        id=1,
    )

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [
        valuation
    ]

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1

    session.execute.side_effect = [
        list_result,
        count_result,
    ]

    items, total = await repository.list_valuations(
        portfolio_id=uuid4(),
        user_id=uuid4(),
        limit=50,
        offset=0,
    )

    assert items == [valuation]
    assert total == 1
    assert session.execute.await_count == 2