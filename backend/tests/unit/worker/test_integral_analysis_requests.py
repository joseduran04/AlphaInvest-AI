from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from alphainvest.core.config import Settings
from alphainvest.worker.jobs.integral_analysis_requests import (
    _handle_processing_failure,
    _process_request,
    process_pending_integral_analysis_requests,
)
from alphainvest.worker.registry import (
    WORKER_JOB_REGISTRY,
)

pytestmark = pytest.mark.unit


def build_settings() -> Settings:
    return cast(
        Settings,
        SimpleNamespace(
            worker_ai_analysis_batch_size=10,
            worker_ai_analysis_lock_seconds=1800,
        ),
    )


def test_integral_job_is_registered() -> None:
    assert (
        "PROCESAR_ANALISIS_INTEGRALES_PENDIENTES"
        in WORKER_JOB_REGISTRY
    )

    assert (
        WORKER_JOB_REGISTRY[
            "PROCESAR_ANALISIS_INTEGRALES_PENDIENTES"
        ]
        is process_pending_integral_analysis_requests
    )


@pytest.mark.asyncio
async def test_integral_job_returns_when_no_pending(
) -> None:
    ai_repository = SimpleNamespace(
        list_running_integral_analysis_requests=AsyncMock(
            return_value=[]
        ),
        list_pending_integral_analysis_requests=AsyncMock(
            return_value=[]
        ),
        commit=AsyncMock(),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(
            return_value=SimpleNamespace(
                maximo_reintentos=3
            )
        ),
        mark_expired_process_locks=AsyncMock(
            return_value=0
        ),
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=ai_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "OperationRepository"
            ),
            return_value=operation_repository,
        ),
    ):
        await process_pending_integral_analysis_requests(
            build_settings()
        )

    (
        ai_repository
        .list_pending_integral_analysis_requests
        .assert_awaited_once_with(
            limit=10
        )
    )


@pytest.mark.asyncio
async def test_integral_job_recovers_orphan_request(
) -> None:
    request = SimpleNamespace(
        id=uuid4(),
        intentos_procesamiento=1,
        porcentaje_progreso=10,
    )

    ai_repository = SimpleNamespace(
        list_running_integral_analysis_requests=AsyncMock(
            return_value=[request]
        ),
        reset_analysis_request_for_retry=AsyncMock(),
        list_pending_integral_analysis_requests=AsyncMock(
            return_value=[]
        ),
        commit=AsyncMock(),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(
            return_value=SimpleNamespace(
                maximo_reintentos=3
            )
        ),
        mark_expired_process_locks=AsyncMock(
            return_value=0
        ),
        is_process_lock_active=AsyncMock(
            return_value=False
        ),
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=ai_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "OperationRepository"
            ),
            return_value=operation_repository,
        ),
    ):
        await process_pending_integral_analysis_requests(
            build_settings()
        )

    (
        ai_repository
        .reset_analysis_request_for_retry
        .assert_awaited_once_with(
            request
        )
    )


@pytest.mark.asyncio
async def test_orphan_integral_fails_after_max_attempts(
) -> None:
    request = SimpleNamespace(
        id=uuid4(),
        intentos_procesamiento=4,
        porcentaje_progreso=50,
    )

    ai_repository = SimpleNamespace(
        list_running_integral_analysis_requests=AsyncMock(
            return_value=[request]
        ),
        update_analysis_request_status=AsyncMock(),
        list_pending_integral_analysis_requests=AsyncMock(
            return_value=[]
        ),
        commit=AsyncMock(),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(
            return_value=SimpleNamespace(
                maximo_reintentos=3
            )
        ),
        mark_expired_process_locks=AsyncMock(
            return_value=0
        ),
        is_process_lock_active=AsyncMock(
            return_value=False
        ),
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=ai_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "OperationRepository"
            ),
            return_value=operation_repository,
        ),
    ):
        await process_pending_integral_analysis_requests(
            build_settings()
        )

    call = (
        ai_repository
        .update_analysis_request_status
        .await_args
    )

    assert call is not None

    assert (
        call.kwargs["status"]
        == "FALLIDA"
    )


@pytest.mark.asyncio
async def test_skips_integral_when_lock_not_acquired(
) -> None:
    request_id = uuid4()

    operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=False
        ),
        rollback=AsyncMock(),
        commit=AsyncMock(),
        release_process_lock=AsyncMock(),
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "MarketRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "ProfileRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "PortfolioRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "OperationRepository"
            ),
            return_value=operation_repository,
        ),
        patch(
            
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "IntegralAnalysisProcessor"
            
        ) as processor_class,
    ):
        processor_class.return_value.process = (
            AsyncMock()
        )

        await _process_request(
            settings=build_settings(),
            analysis_request_id=request_id,
            max_attempts=4,
        )

    (
        operation_repository
        .rollback
        .assert_awaited_once()
    )

    (
        processor_class
        .return_value
        .process
        .assert_not_awaited()
    )

    (
        operation_repository
        .release_process_lock
        .assert_not_awaited()
    )


@pytest.mark.asyncio
async def test_failure_resets_integral_before_max_attempts(
) -> None:
    request_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        intentos_procesamiento=1,
        porcentaje_progreso=10,
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        reset_analysis_request_for_retry=AsyncMock(),
        update_analysis_request_status=AsyncMock(),
        commit=AsyncMock(),
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=repository,
        ),
    ):
        await _handle_processing_failure(
            analysis_request_id=request_id,
            max_attempts=4,
            error=RuntimeError(
                "fallo temporal"
            ),
        )

    (
        repository
        .reset_analysis_request_for_retry
        .assert_awaited_once_with(
            request
        )
    )

    (
        repository
        .update_analysis_request_status
        .assert_not_awaited()
    )

    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_failure_marks_integral_failed_at_max_attempts(
) -> None:
    request_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        intentos_procesamiento=4,
        porcentaje_progreso=50,
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        reset_analysis_request_for_retry=AsyncMock(),
        update_analysis_request_status=AsyncMock(),
        commit=AsyncMock(),
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=repository,
        ),
    ):
        await _handle_processing_failure(
            analysis_request_id=request_id,
            max_attempts=4,
            error=RuntimeError(
                "fallo definitivo"
            ),
        )

    call = (
        repository
        .update_analysis_request_status
        .await_args
    )

    assert call is not None

    assert (
        call.kwargs["status"]
        == "FALLIDA"
    )

    assert (
        call.kwargs["error_message"]
        == "fallo definitivo"
    )

    (
        repository
        .reset_analysis_request_for_retry
        .assert_not_awaited()
    )

    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_integral_creates_notification_after_success(
) -> None:
    request_id = uuid4()
    user_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        usuario_id=user_id,
        estado="PENDIENTE",
        intentos_procesamiento=0,
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
    )

    operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        release_process_lock=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    notification_service = SimpleNamespace(
        create_application_notification_once=(
            AsyncMock()
        )
    )

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=ai_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "MarketRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "ProfileRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "PortfolioRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "OperationRepository"
            ),
            return_value=operation_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "RecommendationProcessor"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "IntegralAnalysisProcessor"
            ),
        ) as processor_class,
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "NotificationService"
            ),
            return_value=notification_service,
        ),
    ):
        processor_class.return_value.process = (
            AsyncMock()
        )

        await _process_request(
            settings=build_settings(),
            analysis_request_id=request_id,
            max_attempts=4,
        )

    (
        processor_class
        .return_value
        .process
        .assert_awaited_once_with(
            request_id=request_id
        )
    )

    (
        notification_service
        .create_application_notification_once
        .assert_awaited_once()
    )

    call = (
        notification_service
        .create_application_notification_once
        .await_args
    )

    assert call is not None

    assert call.kwargs[
        "user_id"
    ] == user_id

    assert call.kwargs[
        "reference_type"
    ] == "ANALISIS_INTEGRAL"

    assert call.kwargs[
        "reference_id"
    ] == str(request_id)


@pytest.mark.asyncio
async def test_integral_notification_failure_does_not_fail_request(
) -> None:
    request_id = uuid4()
    user_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        usuario_id=user_id,
        estado="PENDIENTE",
        intentos_procesamiento=0,
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
    )

    operation_repository = SimpleNamespace(
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        release_process_lock=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
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

    context = AsyncMock()
    context.__aenter__.return_value = (
        SimpleNamespace()
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AsyncSessionFactory"
            ),
            return_value=context,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "AIRepository"
            ),
            return_value=ai_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "MarketRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "ProfileRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "PortfolioRepository"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "OperationRepository"
            ),
            return_value=operation_repository,
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "RecommendationProcessor"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "IntegralAnalysisProcessor"
            ),
        ) as processor_class,
        patch(
            (
                "alphainvest.worker.jobs."
                "integral_analysis_requests."
                "NotificationService"
            ),
            return_value=notification_service,
        ),
    ):
        processor_class.return_value.process = (
            AsyncMock()
        )

        await _process_request(
            settings=build_settings(),
            analysis_request_id=request_id,
            max_attempts=4,
        )

    (
        processor_class
        .return_value
        .process
        .assert_awaited_once_with(
            request_id=request_id
        )
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

    operation_repository.rollback.assert_awaited()

    assert operation_repository.commit.await_count >= 2