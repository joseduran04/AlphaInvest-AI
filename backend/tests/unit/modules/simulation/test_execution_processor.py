from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.application.execution_processor import (
    HistoricalExecutionProcessor,
)
from alphainvest.modules.simulation.domain.exceptions import (
    SimulationHistoricalPriceNotFoundError,
)
from alphainvest.modules.simulation.domain.historical import (
    HistoricalAssetInput,
    HistoricalPricePoint,
)

pytestmark = pytest.mark.unit


def build_configuration() -> SimpleNamespace:
    asset_id = uuid4()

    configuration_asset = SimpleNamespace(
        activo_id=asset_id,
        porcentaje_asignado=Decimal("100"),
    )

    return SimpleNamespace(
        id=uuid4(),
        tipo_simulacion="HISTORICA",
        capital_inicial=Decimal("1000"),
        moneda_base="USD",
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2024, 1, 3),
        aportacion_periodica=Decimal("0"),
        frecuencia_aportacion=None,
        comision_porcentaje=Decimal("0"),
        tasa_libre_riesgo=Decimal("4"),
        activos=[
            configuration_asset,
        ],
    )


def build_execution(
    *,
    status: str = "PENDIENTE",
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        estado=status,
        mensaje_error=None,
        configuracion=build_configuration(),
    )


def build_history(
    *,
    asset_id,
) -> HistoricalAssetInput:
    return HistoricalAssetInput(
        asset_id=asset_id,
        assigned_percentage=Decimal("100"),
        prices=(
            HistoricalPricePoint(
                date=date(2024, 1, 1),
                price=Decimal("100"),
            ),
            HistoricalPricePoint(
                date=date(2024, 1, 2),
                price=Decimal("105"),
            ),
            HistoricalPricePoint(
                date=date(2024, 1, 3),
                price=Decimal("110"),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_process_historical_execution(
) -> None:
    execution = build_execution()
    asset_id = (
        execution.configuracion.activos[0].activo_id
    )

    persisted_result = SimpleNamespace(
        id=uuid4()
    )

    repository = SimpleNamespace(
        get_execution_by_id_for_processing=AsyncMock(
            return_value=execution
        ),
        mark_execution_running=AsyncMock(
            return_value=execution
        ),
        create_result=AsyncMock(
            return_value=persisted_result
        ),
        create_asset_result=AsyncMock(),
        mark_execution_completed=AsyncMock(
            return_value=execution
        ),
        mark_execution_failed=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    historical_data_service = SimpleNamespace(
        load_asset_history=AsyncMock(
            return_value=build_history(
                asset_id=asset_id
            )
        )
    )

    processor = HistoricalExecutionProcessor(
        repository=repository,
        historical_data_service=(
            historical_data_service
        ),
    )

    response = await processor.process(
        execution_id=execution.id
    )

    assert response is persisted_result

    repository.mark_execution_running.assert_awaited_once_with(
        execution
    )

    repository.create_result.assert_awaited_once()

    repository.create_asset_result.assert_awaited_once()

    repository.mark_execution_completed.assert_awaited_once_with(
        execution
    )

    assert repository.commit.await_count == 2

    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_marks_execution_failed(
) -> None:
    execution = build_execution()

    repository = SimpleNamespace(
        get_execution_by_id_for_processing=AsyncMock(
            side_effect=[
                execution,
                execution,
            ]
        ),
        mark_execution_running=AsyncMock(
            return_value=execution
        ),
        create_result=AsyncMock(),
        create_asset_result=AsyncMock(),
        mark_execution_completed=AsyncMock(),
        mark_execution_failed=AsyncMock(
            return_value=execution
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    historical_data_service = SimpleNamespace(
        load_asset_history=AsyncMock(
            side_effect=(
                SimulationHistoricalPriceNotFoundError(
                    "No existen precios históricos"
                )
            )
        )
    )

    processor = HistoricalExecutionProcessor(
        repository=repository,
        historical_data_service=(
            historical_data_service
        ),
    )

    with pytest.raises(
        SimulationHistoricalPriceNotFoundError
    ):
        await processor.process(
            execution_id=execution.id
        )

    repository.rollback.assert_awaited_once()

    repository.mark_execution_failed.assert_awaited_once_with(
        execution,
        error_message=(
            "No existen precios históricos"
        ),
    )

    assert repository.commit.await_count == 2

    repository.create_result.assert_not_awaited()

    repository.mark_execution_completed.assert_not_awaited()