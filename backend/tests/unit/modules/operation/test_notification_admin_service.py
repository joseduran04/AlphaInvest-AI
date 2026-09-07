from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.operation.application.notification_admin_service import (
    NotificationAdminService,
)
from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.domain.exceptions import (
    InvalidNotificationStateTransitionError,
    NotificationNotFoundError,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

pytestmark = pytest.mark.unit


def build_notification(
    *,
    notification_status: NotificationStatus,
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        tipo=NotificationType.SYSTEM.value,
        canal=NotificationChannel.APPLICATION.value,
        titulo="Notificación de prueba",
        mensaje="Mensaje de prueba",
        prioridad=NotificationPriority.NORMAL.value,
        estado=notification_status.value,
        datos=None,
        fecha_creacion=now,
        fecha_programada=(
            now
            if notification_status
            == NotificationStatus.SCHEDULED
            else None
        ),
        fecha_envio=(
            now
            if notification_status
            == NotificationStatus.SENT
            else None
        ),
        fecha_lectura=None,
        intentos_envio=0,
        ultimo_error=(
            "Error de prueba"
            if notification_status
            == NotificationStatus.FAILED
            else None
        ),
        referencia_tipo=None,
        referencia_id=None,
    )


@pytest.mark.asyncio
async def test_get_notification() -> None:
    notification = build_notification(
        notification_status=NotificationStatus.PENDING
    )

    get_mock = AsyncMock(
        return_value=notification
    )

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification=get_mock,
        ),
    )

    service = NotificationAdminService(
        repository
    )

    result = await service.get_notification(
        notification_id=notification.id
    )

    assert result.id == notification.id

    get_mock.assert_awaited_once_with(
        notification_id=notification.id
    )


@pytest.mark.asyncio
async def test_get_notification_not_found() -> None:
    notification_id = uuid4()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification=AsyncMock(
                return_value=None
            ),
        ),
    )

    service = NotificationAdminService(
        repository
    )

    with pytest.raises(
        NotificationNotFoundError
    ):
        await service.get_notification(
            notification_id=notification_id
        )


@pytest.mark.asyncio
async def test_list_notifications() -> None:
    notification = build_notification(
        notification_status=NotificationStatus.PENDING
    )

    list_mock = AsyncMock(
        return_value=(
            [notification],
            1,
        )
    )

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            list_notifications=list_mock,
        ),
    )

    service = NotificationAdminService(
        repository
    )

    result = await service.list_notifications(
        user_id=notification.usuario_id,
        status=NotificationStatus.PENDING,
        notification_type=NotificationType.SYSTEM,
        channel=NotificationChannel.APPLICATION,
        limit=20,
        offset=0,
    )

    assert result.total == 1
    assert len(result.items) == 1

    list_mock.assert_awaited_once_with(
        user_id=notification.usuario_id,
        status=NotificationStatus.PENDING,
        notification_type=NotificationType.SYSTEM,
        channel=NotificationChannel.APPLICATION,
        limit=20,
        offset=0,
    )


@pytest.mark.parametrize(
    "notification_status",
    [
        NotificationStatus.PENDING,
        NotificationStatus.SCHEDULED,
    ],
)
@pytest.mark.asyncio
async def test_cancel_notification_allowed(
    notification_status: NotificationStatus,
) -> None:
    notification = build_notification(
        notification_status=notification_status
    )

    cancelled = build_notification(
        notification_status=NotificationStatus.CANCELLED
    )
    cancelled.id = notification.id
    cancelled.usuario_id = notification.usuario_id

    get_mock = AsyncMock(
        return_value=notification
    )

    cancel_mock = AsyncMock(
        return_value=cancelled
    )

    commit_mock = AsyncMock()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification=get_mock,
            cancel_notification=cancel_mock,
            commit=commit_mock,
        ),
    )

    service = NotificationAdminService(
        repository
    )

    result = await service.cancel_notification(
        notification_id=notification.id
    )

    assert result.status == NotificationStatus.CANCELLED

    cancel_mock.assert_awaited_once_with(
        notification
    )

    commit_mock.assert_awaited_once()


@pytest.mark.parametrize(
    "notification_status",
    [
        NotificationStatus.SENDING,
        NotificationStatus.SENT,
        NotificationStatus.FAILED,
        NotificationStatus.CANCELLED,
    ],
)
@pytest.mark.asyncio
async def test_cancel_notification_rejects_invalid_status(
    notification_status: NotificationStatus,
) -> None:
    notification = build_notification(
        notification_status=notification_status
    )

    cancel_mock = AsyncMock()
    commit_mock = AsyncMock()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification=AsyncMock(
                return_value=notification
            ),
            cancel_notification=cancel_mock,
            commit=commit_mock,
        ),
    )

    service = NotificationAdminService(
        repository
    )

    with pytest.raises(
        InvalidNotificationStateTransitionError
    ):
        await service.cancel_notification(
            notification_id=notification.id
        )

    cancel_mock.assert_not_awaited()
    commit_mock.assert_not_awaited()