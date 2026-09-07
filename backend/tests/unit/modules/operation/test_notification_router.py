from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi import (
    FastAPI,
    HTTPException,
    status,
)
from fastapi.testclient import TestClient

from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.domain.exceptions import (
    InvalidNotificationStateTransitionError,
    NotificationNotFoundError,
    NotificationNotSentError,
)
from alphainvest.modules.operation.presentation.dependencies import (
    get_notification_admin_service,
    get_notification_service,
    notification_admin_permission,
    notification_read_permission,
)
from alphainvest.modules.operation.presentation.router import (
    router,
)
from alphainvest.modules.operation.presentation.schemas import (
    AdminNotificationListResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadNotificationCountResponse,
)

pytestmark = pytest.mark.unit


def build_notification_response(
    *,
    user_id: UUID,
    notification_id: UUID | None = None,
    read: bool = False,
) -> NotificationResponse:
    now = datetime.now(UTC)

    return NotificationResponse.model_validate(
        SimpleNamespace(
            id=notification_id or uuid4(),
            usuario_id=user_id,
            tipo=(
                NotificationType.RECOMMENDATION.value
            ),
            canal=(
                NotificationChannel.APPLICATION.value
            ),
            titulo="Nueva recomendación",
            mensaje=(
                "Tienes una nueva recomendación "
                "disponible."
            ),
            prioridad=(
                NotificationPriority.NORMAL.value
            ),
            estado=NotificationStatus.SENT.value,
            datos={
                "asset": "AAPL",
            },
            fecha_creacion=now,
            fecha_programada=None,
            fecha_envio=now,
            fecha_lectura=(
                now if read else None
            ),
            intentos_envio=0,
            ultimo_error=None,
            referencia_tipo="RECOMENDACION",
            referencia_id=(
                "recommendation-id"
            ),
        )
    )


def build_app(
    service: object,
    *,
    user_id: UUID | None = None,
) -> FastAPI:
    app = FastAPI()

    app.include_router(
        router
    )

    app.dependency_overrides[
        get_notification_service
    ] = lambda: service

    authenticated_user_id = (
        user_id or uuid4()
    )

    app.dependency_overrides[
        notification_read_permission
    ] = lambda: SimpleNamespace(
        user=SimpleNamespace(
            id=authenticated_user_id
        )
    )

    return app


def test_list_notifications() -> None:
    user_id = uuid4()

    list_mock = AsyncMock(
        return_value=NotificationListResponse(
            items=[],
            total=0,
            limit=20,
            offset=0,
            unread_only=False,
        )
    )

    service = SimpleNamespace(
        list_notifications=list_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.get(
        "/notifications"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["items"] == []
    assert payload["total"] == 0
    assert payload["limit"] == 20
    assert payload["offset"] == 0
    assert payload["unread_only"] is False

    list_mock.assert_awaited_once_with(
        user_id=user_id,
        unread_only=False,
        limit=20,
        offset=0,
    )


def test_list_notifications_passes_filters(
) -> None:
    user_id = uuid4()

    list_mock = AsyncMock(
        return_value=NotificationListResponse(
            items=[],
            total=0,
            limit=10,
            offset=5,
            unread_only=True,
        )
    )

    service = SimpleNamespace(
        list_notifications=list_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.get(
        
            "/notifications"
            "?unread_only=true"
            "&limit=10"
            "&offset=5"
        
    )

    assert response.status_code == 200

    list_mock.assert_awaited_once_with(
        user_id=user_id,
        unread_only=True,
        limit=10,
        offset=5,
    )


@pytest.mark.parametrize(
    ("query", "expected_status"),
    [
        ("?limit=0", 422),
        ("?limit=101", 422),
        ("?offset=-1", 422),
    ],
)
def test_list_notifications_rejects_invalid_pagination(
    query: str,
    expected_status: int,
) -> None:
    service = SimpleNamespace(
        list_notifications=AsyncMock()
    )

    app = build_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.get(
        f"/notifications{query}"
    )

    assert response.status_code == (
        expected_status
    )


def test_count_unread_notifications() -> None:
    user_id = uuid4()

    count_mock = AsyncMock(
        return_value=(
            UnreadNotificationCountResponse(
                unread=3
            )
        )
    )

    service = SimpleNamespace(
        count_unread=count_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.get(
        "/notifications/unread-count"
    )

    assert response.status_code == 200
    assert response.json() == {
        "unread": 3,
    }

    count_mock.assert_awaited_once_with(
        user_id=user_id
    )


def test_get_notification() -> None:
    user_id = uuid4()
    notification_id = uuid4()

    notification = build_notification_response(
        user_id=user_id,
        notification_id=notification_id,
    )

    get_mock = AsyncMock(
        return_value=notification
    )

    service = SimpleNamespace(
        get_notification=get_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.get(
        
            "/notifications/"
            f"{notification_id}"
        
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["id"] == str(
        notification_id
    )
    assert payload["user_id"] == str(
        user_id
    )
    assert payload["status"] == (
        NotificationStatus.SENT.value
    )

    get_mock.assert_awaited_once_with(
        notification_id=notification_id,
        user_id=user_id,
    )


def test_get_notification_maps_not_found_to_404(
) -> None:
    user_id = uuid4()
    notification_id = uuid4()

    get_mock = AsyncMock(
        side_effect=NotificationNotFoundError(
            "La notificación solicitada no existe"
        )
    )

    service = SimpleNamespace(
        get_notification=get_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.get(
        
            "/notifications/"
            f"{notification_id}"
        
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "La notificación solicitada no existe"
    )


def test_get_notification_maps_unsent_to_409(
) -> None:
    user_id = uuid4()
    notification_id = uuid4()

    get_mock = AsyncMock(
        side_effect=NotificationNotSentError(
            "La notificación todavía "
            "no ha sido entregada"
        )
    )

    service = SimpleNamespace(
        get_notification=get_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.get(
        
            "/notifications/"
            f"{notification_id}"
        
    )

    assert response.status_code == 409


def test_mark_notification_as_read() -> None:
    user_id = uuid4()
    notification_id = uuid4()

    notification = build_notification_response(
        user_id=user_id,
        notification_id=notification_id,
        read=True,
    )

    mark_mock = AsyncMock(
        return_value=notification
    )

    service = SimpleNamespace(
        mark_as_read=mark_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.patch(
        
            "/notifications/"
            f"{notification_id}/read"
        
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["id"] == str(
        notification_id
    )
    assert payload["read_at"] is not None

    mark_mock.assert_awaited_once_with(
        notification_id=notification_id,
        user_id=user_id,
    )


def test_mark_notification_read_maps_not_found_to_404(
) -> None:
    user_id = uuid4()
    notification_id = uuid4()

    mark_mock = AsyncMock(
        side_effect=NotificationNotFoundError(
            "La notificación solicitada no existe"
        )
    )

    service = SimpleNamespace(
        mark_as_read=mark_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.patch(
        
            "/notifications/"
            f"{notification_id}/read"
        
    )

    assert response.status_code == 404


def test_mark_notification_read_maps_unsent_to_409(
) -> None:
    user_id = uuid4()
    notification_id = uuid4()

    mark_mock = AsyncMock(
        side_effect=NotificationNotSentError(
            "La notificación todavía "
            "no ha sido entregada"
        )
    )

    service = SimpleNamespace(
        mark_as_read=mark_mock
    )

    app = build_app(
        service,
        user_id=user_id,
    )

    client = TestClient(
        app
    )

    response = client.patch(
        
            "/notifications/"
            f"{notification_id}/read"
        
    )

    assert response.status_code == 409


def test_notification_permission_failure_returns_403(
) -> None:
    service = SimpleNamespace(
        list_notifications=AsyncMock()
    )

    app = FastAPI()

    app.include_router(
        router
    )

    app.dependency_overrides[
        get_notification_service
    ] = lambda: service

    async def deny_permission() -> None:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Permiso insuficiente",
        )

    app.dependency_overrides[
        notification_read_permission
    ] = deny_permission

    client = TestClient(
        app
    )

    response = client.get(
        "/notifications"
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Permiso insuficiente",
    }


def build_admin_app(
    service: object,
) -> FastAPI:
    app = FastAPI()

    app.include_router(
        router
    )

    app.dependency_overrides[
        get_notification_admin_service
    ] = lambda: service

    app.dependency_overrides[
        notification_admin_permission
    ] = lambda: SimpleNamespace(
        user=SimpleNamespace(
            id=uuid4()
        )
    )

    return app


def test_admin_lists_notifications() -> None:
    service = SimpleNamespace(
        list_notifications=AsyncMock(
            return_value=AdminNotificationListResponse(
                items=[],
                total=0,
                limit=20,
                offset=0,
            )
        )
    )

    app = build_admin_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.get(
        "/notifications/admin"
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_admin_get_maps_not_found_to_404() -> None:
    service = SimpleNamespace(
        get_notification=AsyncMock(
            side_effect=NotificationNotFoundError(
                "La notificación solicitada no existe"
            )
        )
    )

    app = build_admin_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.get(
        f"/notifications/admin/{uuid4()}"
    )

    assert response.status_code == 404


def test_admin_cancel_maps_invalid_state_to_409(
) -> None:
    service = SimpleNamespace(
        cancel_notification=AsyncMock(
            side_effect=(
                InvalidNotificationStateTransitionError(
                    "Sólo pueden cancelarse "
                    "notificaciones PENDIENTES "
                    "o PROGRAMADAS"
                )
            )
        )
    )

    app = build_admin_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.patch(
        
            "/notifications/admin/"
            f"{uuid4()}/cancel"
        
    )

    assert response.status_code == 409