from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_list_notifications_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/notifications"
    )

    assert response.status_code == 401


def test_unread_count_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/notifications/unread-count"
    )

    assert response.status_code == 401


def test_get_notification_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        f"/api/v1/notifications/{uuid4()}"
    )

    assert response.status_code == 401


def test_mark_notification_read_requires_authentication(
    client: TestClient,
) -> None:
    response = client.patch(
        
            f"/api/v1/notifications/{uuid4()}"
            "/read"
        
    )

    assert response.status_code == 401