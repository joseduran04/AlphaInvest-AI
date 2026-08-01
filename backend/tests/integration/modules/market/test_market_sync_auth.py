from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_price_sync_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/market/assets/{uuid4()}/prices/sync"
    )

    assert response.status_code == 401