from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from alphainvest.modules.market.application.synchronization_service import (
    PriceSynchronizationService,
)
from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    ProcessLockUnavailableError,
    ScheduledJobNotFoundError,
)
from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)

pytestmark = pytest.mark.unit


def build_price(
    price_date: date,
) -> DailyPricePoint:
    return DailyPricePoint(
        date=price_date,
        open=Decimal("210"),
        high=Decimal("215"),
        low=Decimal("208"),
        close=Decimal("214"),
        adjusted_close=None,
        volume=Decimal("1000"),
        currency="USD",
    )


@pytest.mark.asyncio
async def test_sync_raises_when_asset_missing() -> None:
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=None)
    )
    operation_repository = SimpleNamespace()
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
    )

    service = PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

    with pytest.raises(AssetNotFoundError):
        await service.synchronize_asset(
            asset_id=uuid4(),
            requested_by=uuid4(),
        )


@pytest.mark.asyncio
async def test_sync_raises_when_source_missing() -> None:
    asset_id = uuid4()

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
                moneda="USD",
            )
        ),
        get_financial_source_by_name=AsyncMock(
            return_value=None
        ),
    )
    operation_repository = SimpleNamespace()
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
    )

    service = PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

    with pytest.raises(FinancialSourceNotFoundError):
        await service.synchronize_asset(
            asset_id=asset_id,
            requested_by=uuid4(),
        )


@pytest.mark.asyncio
async def test_sync_raises_when_job_missing() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
        moneda="USD",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
    )
    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(return_value=None)
    )
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
    )

    service = PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

    with pytest.raises(ScheduledJobNotFoundError):
        await service.synchronize_asset(
            asset_id=asset_id,
            requested_by=uuid4(),
        )


@pytest.mark.asyncio
async def test_sync_rejects_concurrent_process() -> None:
    asset_id = uuid4()
    source_id = uuid4()
    job_id = uuid4()

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
        moneda="USD",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
    )
    job = SimpleNamespace(
        id=job_id,
        codigo="ACTUALIZAR_PRECIOS_DIARIOS",
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(return_value=job),
        acquire_process_lock=AsyncMock(
            return_value=False
        ),
        rollback=AsyncMock(),
        create_execution=AsyncMock(),
    )

    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_daily_prices=AsyncMock(),
    )

    service = PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

    with pytest.raises(
        ProcessLockUnavailableError,
        match="ya está siendo sincronizado",
    ):
        await service.synchronize_asset(
            asset_id=asset_id,
            requested_by=uuid4(),
        )

    operation_repository.acquire_process_lock.assert_awaited_once()
    operation_repository.rollback.assert_awaited_once()
    operation_repository.create_execution.assert_not_awaited()
    provider.fetch_daily_prices.assert_not_awaited()


@pytest.mark.asyncio
async def test_sync_creates_and_updates_prices() -> None:
    asset_id = uuid4()
    source_id = uuid4()
    job_id = uuid4()
    execution_id = uuid4()
    requested_by = uuid4()

    first_date = date(2026, 7, 30)
    second_date = date(2026, 7, 31)
    synchronized_at = datetime.now(UTC)

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
        moneda="USD",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
    )
    job = SimpleNamespace(
        id=job_id,
        codigo="ACTUALIZAR_PRECIOS_DIARIOS",
    )
    execution = SimpleNamespace(
        id=execution_id,
    )
    prices = [
        build_price(first_date),
        build_price(second_date),
    ]

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
        get_existing_price_dates=AsyncMock(
            return_value={first_date}
        ),
        upsert_daily_prices=AsyncMock(),
        mark_source_requested=AsyncMock(
            return_value=synchronized_at
        ),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(return_value=job),

        # Adquiere correctamente el bloqueo antes de continuar.
        acquire_process_lock=AsyncMock(
            return_value=True
        ),

        create_execution=AsyncMock(
            return_value=execution
        ),
        mark_completed=AsyncMock(),
        update_job_last_execution=AsyncMock(),

        # Libera el bloqueo cuando la sincronización termina.
        release_process_lock=AsyncMock(
            return_value=True
        ),

        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_daily_prices=AsyncMock(
            return_value=prices
        ),
    )

    service = PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

    result = await service.synchronize_asset(
        asset_id=asset_id,
        requested_by=requested_by,
    )

    assert result.execution_id == execution_id
    assert result.asset_id == asset_id
    assert result.received == 2
    assert result.created == 1
    assert result.updated == 1
    assert result.first_date == first_date
    assert result.last_date == second_date

    operation_repository.acquire_process_lock.assert_awaited_once()
    operation_repository.create_execution.assert_awaited_once()

    provider.fetch_daily_prices.assert_awaited_once_with(
        symbol="AAPL",
        currency="USD",
    )

    market_repository.upsert_daily_prices.assert_awaited_once()
    operation_repository.mark_completed.assert_awaited_once()

    operation_repository.update_job_last_execution.assert_awaited_once_with(
        job
    )

    operation_repository.release_process_lock.assert_awaited_once()

    # Primer commit:
    # guarda el bloqueo y la ejecución EJECUTANDO.
    #
    # Segundo commit:
    # guarda precios, ejecución COMPLETADA y bloqueo LIBERADO.
    assert operation_repository.commit.await_count == 2

    operation_repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_sync_releases_lock_and_records_failure() -> None:
    asset_id = uuid4()
    source_id = uuid4()
    job_id = uuid4()
    execution_id = uuid4()

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
        moneda="USD",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
    )
    job = SimpleNamespace(
        id=job_id,
        codigo="ACTUALIZAR_PRECIOS_DIARIOS",
    )
    execution = SimpleNamespace(
        id=execution_id,
    )
    current_execution = SimpleNamespace(
        id=execution_id,
    )
    prices = [
        build_price(date(2026, 7, 31))
    ]

    database_error = SQLAlchemyError(
        "database error"
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
        get_existing_price_dates=AsyncMock(
            return_value=set()
        ),
        upsert_daily_prices=AsyncMock(
            side_effect=database_error
        ),
        mark_source_requested=AsyncMock(),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(return_value=job),

        # El proceso sí logra adquirir el bloqueo.
        acquire_process_lock=AsyncMock(
            return_value=True
        ),

        create_execution=AsyncMock(
            return_value=execution
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),

        get_execution=AsyncMock(
            return_value=current_execution
        ),
        mark_failed=AsyncMock(),

        # El bloqueo también debe liberarse cuando ocurre un error.
        release_process_lock=AsyncMock(
            return_value=True
        ),
    )

    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_daily_prices=AsyncMock(
            return_value=prices
        ),
    )

    service = PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

    with pytest.raises(SQLAlchemyError):
        await service.synchronize_asset(
            asset_id=asset_id,
            requested_by=uuid4(),
        )

    operation_repository.acquire_process_lock.assert_awaited_once()
    operation_repository.rollback.assert_awaited_once()

    operation_repository.get_execution.assert_awaited_once_with(
        execution_id
    )
    operation_repository.mark_failed.assert_awaited_once()

    # Esta es la validación importante:
    # el bloqueo se libera incluso cuando falla PostgreSQL.
    operation_repository.release_process_lock.assert_awaited_once()

    # Primer commit:
    # ejecución EJECUTANDO.
    #
    # Segundo commit:
    # ejecución FALLIDA y bloqueo LIBERADO.
    assert operation_repository.commit.await_count == 2