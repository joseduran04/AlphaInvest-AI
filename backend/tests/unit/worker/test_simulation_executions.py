from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from alphainvest.core.config import Settings
from alphainvest.worker.jobs.simulation_executions import (
    process_pending_simulation_executions,
)
from alphainvest.worker.registry import (
    WORKER_JOB_REGISTRY,
)

pytestmark = pytest.mark.unit

def test_simulation_job_is_registered() -> None:
    assert (
        "PROCESAR_SIMULACIONES_PENDIENTES"
        in WORKER_JOB_REGISTRY
    )

    assert (
        WORKER_JOB_REGISTRY[
            "PROCESAR_SIMULACIONES_PENDIENTES"
        ]
        is process_pending_simulation_executions
    )

def build_settings() -> Settings:
    return cast(
        Settings,
        SimpleNamespace(
            worker_simulation_batch_size=10,
            worker_simulation_source_name=(
                "Carga Manual"
            ),
        ),
    )


@pytest.mark.asyncio
async def test_simulation_job_returns_when_no_pending(
) -> None:
    repository = SimpleNamespace(
        list_pending_executions_for_processing=(
            AsyncMock(return_value=[])
        )
    )

    session = SimpleNamespace()

    session_context = AsyncMock()
    session_context.__aenter__.return_value = (
        session
    )

    with patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "AsyncSessionFactory"
        ),
        return_value=session_context,
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "SimulationRepository"
        ),
        return_value=repository,
    ):
        await process_pending_simulation_executions(
            build_settings()
        )

    (
        repository
        .list_pending_executions_for_processing
        .assert_awaited_once_with(
            limit=10
        )
    )


@pytest.mark.asyncio
async def test_simulation_job_processes_pending(
) -> None:
    execution = SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        configuracion_id=uuid4(),
    )

    discovery_repository = SimpleNamespace(
        list_pending_executions_for_processing=(
            AsyncMock(
                return_value=[
                    execution,
                ]
            )
        )
    )

    processing_repository = SimpleNamespace()

    operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        release_process_lock=AsyncMock(
            return_value=True
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    processor = SimpleNamespace(
        process=AsyncMock()
    )

    first_context = AsyncMock()
    first_context.__aenter__.return_value = (
        SimpleNamespace()
    )

    second_context = AsyncMock()
    second_context.__aenter__.return_value = (
        SimpleNamespace()
    )

    notification_service = SimpleNamespace(
        create_application_notification_once=(
            AsyncMock()
        )
    )

    with patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "AsyncSessionFactory"
        ),
        side_effect=[
            first_context,
            second_context,
        ],
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "SimulationRepository"
        ),
        side_effect=[
            discovery_repository,
            processing_repository,
        ],
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "OperationRepository"
        ),
        return_value=operation_repository,
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "MarketRepository"
        ),
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "NotificationService"
        ),
        return_value=notification_service,
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "HistoricalDataService"
        ),
    ) as data_service_class, patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "HistoricalExecutionProcessor"
        ),
        return_value=processor,
    ):
        await process_pending_simulation_executions(
            build_settings()
        )

    processor.process.assert_awaited_once_with(
        execution_id=execution.id
    )

    (
        notification_service
        .create_application_notification_once
        .assert_awaited_once()
    )

    notification_call = (
        notification_service
        .create_application_notification_once
        .await_args
    )

    assert notification_call is not None

    assert (
        notification_call.kwargs["user_id"]
        == execution.usuario_id
    )

    assert (
        notification_call.kwargs[
            "reference_type"
        ]
        == "EJECUCION_SIMULACION"
    )

    assert (
        notification_call.kwargs[
            "reference_id"
        ]
        == str(execution.id)
    )

    (
        operation_repository
        .acquire_process_lock
        .assert_awaited_once()
    )

    (
        operation_repository
        .release_process_lock
        .assert_awaited_once()
    )

    assert (
        operation_repository.commit.await_count
        == 2
    )

    operation_repository.rollback.assert_not_awaited()

    assert (
        data_service_class.call_args
        .kwargs["source_name"]
        == "Carga Manual"
    )


@pytest.mark.asyncio
async def test_simulation_job_continues_after_failure(
) -> None:
    first_execution = SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        configuracion_id=uuid4(),
    )

    second_execution = SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        configuracion_id=uuid4(),
    )

    discovery_repository = SimpleNamespace(
        list_pending_executions_for_processing=(
            AsyncMock(
                return_value=[
                    first_execution,
                    second_execution,
                ]
            )
        )
    )

    processor = SimpleNamespace(
        process=AsyncMock(
            side_effect=[
                RuntimeError("fallo"),
                None,
            ]
        )
    )

    first_operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        release_process_lock=AsyncMock(
            return_value=True
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    second_operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        release_process_lock=AsyncMock(
            return_value=True
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    contexts = []

    for _ in range(3):
        context = AsyncMock()
        context.__aenter__.return_value = (
            SimpleNamespace()
        )
        contexts.append(context)

    first_notification_service = (
        SimpleNamespace(
            create_application_notification_once=(
                AsyncMock()
            )
        )
    )

    second_notification_service = (
        SimpleNamespace(
            create_application_notification_once=(
                AsyncMock()
            )
        )
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "NotificationService"
            ),
            side_effect=[
                first_notification_service,
                second_notification_service,
            ],
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "AsyncSessionFactory"
            ),
            side_effect=contexts,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "SimulationRepository"
            ),
            side_effect=[
                discovery_repository,
                SimpleNamespace(),
                SimpleNamespace(),
            ],
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "OperationRepository"
            ),
            side_effect=[
                first_operation_repository,
                second_operation_repository,
            ],
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "MarketRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "HistoricalDataService"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "HistoricalExecutionProcessor"
            ),
            return_value=processor,
        ),
    ):
        await process_pending_simulation_executions(
            build_settings()
        )

    assert processor.process.await_count == 2

    processor.process.assert_any_await(
        execution_id=first_execution.id
    )

    processor.process.assert_any_await(
        execution_id=second_execution.id
    )

    (
        first_operation_repository
        .release_process_lock
        .assert_awaited_once()
    )

    (
        second_operation_repository
        .release_process_lock
        .assert_awaited_once()
    )

    (
        first_notification_service
        .create_application_notification_once
        .assert_not_awaited()
    )

    (
        second_notification_service
        .create_application_notification_once
        .assert_awaited_once()
    )


@pytest.mark.asyncio
async def test_simulation_job_skips_locked_execution(
) -> None:
    execution = SimpleNamespace(
        id=uuid4()
    )

    discovery_repository = SimpleNamespace(
        list_pending_executions_for_processing=(
            AsyncMock(
                return_value=[
                    execution,
                ]
            )
        )
    )

    operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=False
        ),
        release_process_lock=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    processor = SimpleNamespace(
        process=AsyncMock()
    )

    first_context = AsyncMock()
    first_context.__aenter__.return_value = (
        SimpleNamespace()
    )

    second_context = AsyncMock()
    second_context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "AsyncSessionFactory"
        ),
        side_effect=[
            first_context,
            second_context,
        ],
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "SimulationRepository"
        ),
        side_effect=[
            discovery_repository,
            SimpleNamespace(),
        ],
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "OperationRepository"
        ),
        return_value=operation_repository,
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "MarketRepository"
        ),
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "HistoricalDataService"
        ),
    ), patch(
        (
            "alphainvest.worker.jobs."
            "simulation_executions."
            "HistoricalExecutionProcessor"
        ),
        return_value=processor,
    ):
        await process_pending_simulation_executions(
            build_settings()
        )

    (
        operation_repository
        .acquire_process_lock
        .assert_awaited_once()
    )

    processor.process.assert_not_awaited()

    (
        operation_repository
        .release_process_lock
        .assert_not_awaited()
    )

    operation_repository.commit.assert_not_awaited()

    operation_repository.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_simulation_notification_failure_does_not_fail_execution(
) -> None:
    execution = SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        configuracion_id=uuid4(),
    )

    discovery_repository = SimpleNamespace(
        list_pending_executions_for_processing=(
            AsyncMock(
                return_value=[
                    execution,
                ]
            )
        )
    )

    operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        release_process_lock=AsyncMock(
            return_value=True
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    processor = SimpleNamespace(
        process=AsyncMock()
    )

    notification_service = SimpleNamespace(
        create_application_notification_once=(
            AsyncMock(
                side_effect=RuntimeError(
                    "fallo notificación"
                )
            )
        )
    )

    first_context = AsyncMock()
    first_context.__aenter__.return_value = (
        SimpleNamespace()
    )

    second_context = AsyncMock()
    second_context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "AsyncSessionFactory"
            ),
            side_effect=[
                first_context,
                second_context,
            ],
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "SimulationRepository"
            ),
            side_effect=[
                discovery_repository,
                SimpleNamespace(),
            ],
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "OperationRepository"
            ),
            return_value=(
                operation_repository
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "MarketRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "HistoricalDataService"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "HistoricalExecutionProcessor"
            ),
            return_value=processor,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "simulation_executions."
                "NotificationService"
            ),
            return_value=(
                notification_service
            ),
        ),
    ):
        await process_pending_simulation_executions(
            build_settings()
        )

    processor.process.assert_awaited_once_with(
        execution_id=execution.id
    )

    (
        notification_service
        .create_application_notification_once
        .assert_awaited_once()
    )

    (
        operation_repository
        .release_process_lock
        .assert_awaited_once()
    )

    assert (
        operation_repository.rollback.await_count
        >= 1
    )