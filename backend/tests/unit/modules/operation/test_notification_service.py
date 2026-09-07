from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.operation.application.notification_service import (
    NotificationService,
)
from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.domain.exceptions import (
    InvalidNotificationContentError,
    InvalidNotificationReferenceError,
    NotificationNotFoundError,
    NotificationNotSentError,
)
from alphainvest.modules.operation.infrastructure.models import (
    NotificationModel,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

pytestmark = pytest.mark.unit


def build_notification(
    *,
    status: NotificationStatus = NotificationStatus.SENT,
    read: bool = False,
) -> NotificationModel:
    now = datetime.now(UTC)

    return NotificationModel(
        id=uuid4(),
        usuario_id=uuid4(),
        tipo=NotificationType.RECOMMENDATION.value,
        canal=NotificationChannel.APPLICATION.value,
        titulo="Nueva recomendación",
        mensaje="Tienes una nueva recomendación.",
        prioridad=NotificationPriority.NORMAL.value,
        estado=status.value,
        datos={"asset": "AAPL"},
        fecha_creacion=now,
        fecha_programada=None,
        fecha_envio=(
            now
            if status == NotificationStatus.SENT
            else None
        ),
        fecha_lectura=now if read else None,
        intentos_envio=0,
        ultimo_error=None,
        referencia_tipo="RECOMENDACION",
        referencia_id="recommendation-id",
    )


@pytest.mark.asyncio
async def test_create_application_notification() -> None:
    notification = build_notification()

    create_notification_mock = AsyncMock(
        return_value=notification
    )
    commit_mock = AsyncMock()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            create_notification=create_notification_mock,
            commit=commit_mock,
        ),
    )

    service = NotificationService(repository)

    response = (
        await service.create_application_notification(
            user_id=notification.usuario_id,
            notification_type=(
                NotificationType.RECOMMENDATION
            ),
            title="  Nueva recomendación  ",
            message=(
                "  Tienes una nueva recomendación.  "
            ),
            reference_type="RECOMENDACION",
            reference_id="recommendation-id",
        )
    )

    assert response.id == notification.id

    create_notification_mock.assert_awaited_once_with(
        user_id=notification.usuario_id,
        notification_type=(
            NotificationType.RECOMMENDATION
        ),
        channel=NotificationChannel.APPLICATION,
        title="Nueva recomendación",
        message="Tienes una nueva recomendación.",
        priority=NotificationPriority.NORMAL,
        status=NotificationStatus.SENT,
        data=None,
        scheduled_at=None,
        reference_type="RECOMENDACION",
        reference_id="recommendation-id",
    )

    commit_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_rejects_empty_title() -> None:
    repository = cast(
        OperationRepository,
        SimpleNamespace(),
    )

    service = NotificationService(repository)

    with pytest.raises(
        InvalidNotificationContentError
    ):
        await service.create_application_notification(
            user_id=uuid4(),
            notification_type=NotificationType.SYSTEM,
            title="   ",
            message="Mensaje",
        )


@pytest.mark.asyncio
async def test_create_rejects_incomplete_reference() -> None:
    repository = cast(
        OperationRepository,
        SimpleNamespace(),
    )

    service = NotificationService(repository)

    with pytest.raises(
        InvalidNotificationReferenceError
    ):
        await service.create_application_notification(
            user_id=uuid4(),
            notification_type=NotificationType.SYSTEM,
            title="Título",
            message="Mensaje",
            reference_type="RECOMENDACION",
            reference_id=None,
        )


@pytest.mark.asyncio
async def test_get_notification() -> None:
    notification = build_notification()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification_for_user=AsyncMock(
                return_value=notification
            )
        ),
    )

    service = NotificationService(repository)

    response = await service.get_notification(
        notification_id=notification.id,
        user_id=notification.usuario_id,
    )

    assert response.id == notification.id


def test_application_channel_is_supported() -> None:
    assert NotificationService.is_channel_supported(
        NotificationChannel.APPLICATION
    )


def test_email_channel_is_not_supported() -> None:
    assert not NotificationService.is_channel_supported(
        NotificationChannel.EMAIL
    )


def test_push_channel_is_not_supported() -> None:
    assert not NotificationService.is_channel_supported(
        NotificationChannel.PUSH
    )


def test_supported_channels_only_contains_application(
) -> None:
    assert NotificationService.supported_channels() == (
        NotificationChannel.APPLICATION,
    )


@pytest.mark.asyncio
async def test_get_notification_not_found() -> None:
    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification_for_user=AsyncMock(
                return_value=None
            )
        ),
    )

    service = NotificationService(repository)

    with pytest.raises(
        NotificationNotFoundError
    ):
        await service.get_notification(
            notification_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_rejects_unsent_notification() -> None:
    notification = build_notification(
        status=NotificationStatus.PENDING
    )

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification_for_user=AsyncMock(
                return_value=notification
            )
        ),
    )

    service = NotificationService(repository)

    with pytest.raises(
        NotificationNotSentError
    ):
        await service.get_notification(
            notification_id=notification.id,
            user_id=notification.usuario_id,
        )


@pytest.mark.asyncio
async def test_list_notifications() -> None:
    notification = build_notification()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            list_notifications_for_user=AsyncMock(
                return_value=(
                    [notification],
                    1,
                )
            )
        ),
    )

    service = NotificationService(repository)

    response = await service.list_notifications(
        user_id=notification.usuario_id,
        unread_only=True,
        limit=20,
        offset=0,
    )

    assert response.total == 1
    assert response.unread_only is True
    assert response.items[0].id == notification.id


@pytest.mark.asyncio
async def test_count_unread() -> None:
    repository = cast(
        OperationRepository,
        SimpleNamespace(
            count_unread_notifications=AsyncMock(
                return_value=3
            )
        ),
    )

    service = NotificationService(repository)

    response = await service.count_unread(
        user_id=uuid4()
    )

    assert response.unread == 3


@pytest.mark.asyncio
async def test_mark_as_read() -> None:
    notification = build_notification()

    read_notification = build_notification(
        read=True
    )
    read_notification.id = notification.id
    read_notification.usuario_id = (
        notification.usuario_id
    )

    get_notification_mock = AsyncMock(
        return_value=notification
    )
    mark_notification_read_mock = AsyncMock(
        return_value=read_notification
    )
    commit_mock = AsyncMock()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification_for_user=(
                get_notification_mock
            ),
            mark_notification_read=(
                mark_notification_read_mock
            ),
            commit=commit_mock,
        ),
    )

    service = NotificationService(repository)

    response = await service.mark_as_read(
        notification_id=notification.id,
        user_id=notification.usuario_id,
    )

    assert response.read_at is not None

    mark_notification_read_mock.assert_awaited_once_with(
        notification
    )
    commit_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_as_read_is_idempotent() -> None:
    notification = build_notification(
        read=True
    )

    get_notification_mock = AsyncMock(
        return_value=notification
    )
    mark_notification_read_mock = AsyncMock()
    commit_mock = AsyncMock()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification_for_user=(
                get_notification_mock
            ),
            mark_notification_read=(
                mark_notification_read_mock
            ),
            commit=commit_mock,
        ),
    )

    service = NotificationService(repository)

    response = await service.mark_as_read(
        notification_id=notification.id,
        user_id=notification.usuario_id,
    )

    assert response.read_at is not None

    mark_notification_read_mock.assert_not_awaited()
    commit_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_as_read_rejects_unsent() -> None:
    notification = build_notification(
        status=NotificationStatus.PENDING
    )

    get_notification_mock = AsyncMock(
        return_value=notification
    )
    mark_notification_read_mock = AsyncMock()
    commit_mock = AsyncMock()

    repository = cast(
        OperationRepository,
        SimpleNamespace(
            get_notification_for_user=(
                get_notification_mock
            ),
            mark_notification_read=(
                mark_notification_read_mock
            ),
            commit=commit_mock,
        ),
    )

    service = NotificationService(repository)

    with pytest.raises(
        NotificationNotSentError
    ):
        await service.mark_as_read(
            notification_id=notification.id,
            user_id=notification.usuario_id,
        )

    mark_notification_read_mock.assert_not_awaited()
    commit_mock.assert_not_awaited()