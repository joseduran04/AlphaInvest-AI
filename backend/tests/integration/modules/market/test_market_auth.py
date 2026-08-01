from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/market/markets",
        "/api/v1/market/asset-types",
        "/api/v1/market/assets",
        "/api/v1/market/sources",
        f"/api/v1/market/assets/{uuid4()}",
        f"/api/v1/market/assets/{uuid4()}/prices",
        f"/api/v1/market/assets/{uuid4()}/latest-price",
    ],
)
def test_market_endpoints_require_authentication(
    client: TestClient,
    path: str,
) -> None:
    response = client.get(path)

    assert response.status_code == 401