from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.infrastructure.models import (
    NotificationModel,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_acquire_process_lock_returns_true() -> None:
    result = SimpleNamespace(
        scalar_one=lambda: True
    )
    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )
    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    acquired = await repository.acquire_process_lock(
        process_type="CARGA_MERCADO",
        lock_key="MARKET_PRICE_SYNC:asset-id",
        owner="alphainvest-api",
        process_id="process-id",
        duration_seconds=120,
        entity_type="ACTIVO",
        entity_id="asset-id",
        metadata={"symbol": "AAPL"},
    )

    assert acquired is True
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_release_process_lock_returns_true() -> None:
    result = SimpleNamespace(
        scalar_one=lambda: True
    )
    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )
    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    released = await repository.release_process_lock(
        lock_key="MARKET_PRICE_SYNC:asset-id",
        process_id="process-id",
    )

    assert released is True
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_notification() -> None:
    user_id = uuid4()

    session = SimpleNamespace(
        add=Mock(),
        flush=AsyncMock(),
        refresh=AsyncMock(),
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    notification = await repository.create_notification(
        user_id=user_id,
        notification_type=NotificationType.RECOMMENDATION,
        channel=NotificationChannel.APPLICATION,
        title="Nueva recomendación",
        message="Tienes una nueva recomendación disponible.",
        priority=NotificationPriority.NORMAL,
        status=NotificationStatus.PENDING,
        data={"asset": "AAPL"},
        reference_type="RECOMENDACION",
        reference_id="recommendation-id",
    )

    assert notification.usuario_id == user_id
    assert (
        notification.tipo
        == NotificationType.RECOMMENDATION.value
    )
    assert (
        notification.canal
        == NotificationChannel.APPLICATION.value
    )
    assert notification.titulo == "Nueva recomendación"
    assert (
        notification.prioridad
        == NotificationPriority.NORMAL.value
    )
    assert (
        notification.estado
        == NotificationStatus.PENDING.value
    )
    assert notification.datos == {"asset": "AAPL"}
    assert notification.referencia_tipo == "RECOMENDACION"
    assert notification.referencia_id == "recommendation-id"

    session.add.assert_called_once_with(notification)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(notification)


@pytest.mark.asyncio
async def test_get_notification_for_user() -> None:
    notification = NotificationModel(
        id=uuid4(),
        usuario_id=uuid4(),
        tipo=NotificationType.RECOMMENDATION.value,
        canal=NotificationChannel.APPLICATION.value,
        titulo="Nueva recomendación",
        mensaje="Tienes una nueva recomendación disponible.",
        prioridad=NotificationPriority.NORMAL.value,
        estado=NotificationStatus.SENT.value,
    )

    result = SimpleNamespace(
        scalar_one_or_none=lambda: notification
    )

    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    returned = await repository.get_notification_for_user(
        notification_id=notification.id,
        user_id=uuid4(),
    )

    assert returned is notification
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_notification_for_user_returns_none() -> None:
    result = SimpleNamespace(
        scalar_one_or_none=lambda: None
    )

    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    returned = await repository.get_notification_for_user(
        notification_id=uuid4(),
        user_id=uuid4(),
    )

    assert returned is None


@pytest.mark.asyncio
async def test_list_notifications_for_user() -> None:
    notifications = [
        SimpleNamespace(id=uuid4()),
        SimpleNamespace(id=uuid4()),
    ]

    rows_result = SimpleNamespace(
        scalars=lambda: SimpleNamespace(
            all=lambda: notifications
        )
    )

    count_result = SimpleNamespace(
        scalar_one=lambda: 2
    )

    session = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                rows_result,
                count_result,
            ]
        )
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    items, total = (
        await repository.list_notifications_for_user(
            user_id=uuid4(),
            unread_only=False,
            limit=20,
            offset=0,
        )
    )

    assert items == notifications
    assert total == 2
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_list_unread_notifications_for_user() -> None:
    notifications = [
        SimpleNamespace(id=uuid4()),
    ]

    rows_result = SimpleNamespace(
        scalars=lambda: SimpleNamespace(
            all=lambda: notifications
        )
    )

    count_result = SimpleNamespace(
        scalar_one=lambda: 1
    )

    session = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                rows_result,
                count_result,
            ]
        )
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    items, total = (
        await repository.list_notifications_for_user(
            user_id=uuid4(),
            unread_only=True,
            limit=20,
            offset=0,
        )
    )

    assert items == notifications
    assert total == 1
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_count_unread_notifications() -> None:
    result = SimpleNamespace(
        scalar_one=lambda: 3
    )

    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    total = await repository.count_unread_notifications(
        user_id=uuid4(),
    )

    assert total == 3
    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_mark_notification_read() -> None:
    notification = NotificationModel(
        id=uuid4(),
        usuario_id=uuid4(),
        tipo=NotificationType.SYSTEM.value,
        canal=NotificationChannel.APPLICATION.value,
        titulo="Notificación",
        mensaje="Mensaje de prueba.",
        prioridad=NotificationPriority.NORMAL.value,
        estado=NotificationStatus.SENT.value,
    )

    session = SimpleNamespace(
        flush=AsyncMock(),
        refresh=AsyncMock(),
    )

    repository = OperationRepository(
        cast(AsyncSession, session)
    )

    returned = await repository.mark_notification_read(
        notification
    )

    assert returned is notification
    assert notification.fecha_lectura is not None

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(notification)