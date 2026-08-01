from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_synchronization_list_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/market/synchronizations"
    )

    assert response.status_code == 401


def test_synchronization_detail_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        f"/api/v1/market/synchronizations/{uuid4()}"
    )

    assert response.status_code == 401