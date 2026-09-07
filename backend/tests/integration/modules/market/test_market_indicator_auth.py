from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_indicator_calculation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        (
            f"/api/v1/market/assets/{uuid4()}"
            "/indicators/calculate"
        ),
        json={
            "source_id": str(uuid4()),
            "calculations": [
                {
                    "indicator_type": "SMA",
                    "period": 20,
                }
            ],
        },
    )

    assert response.status_code == 401


def test_indicator_list_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            f"/api/v1/market/assets/{uuid4()}"
            "/indicators"
        
    )

    assert response.status_code == 401