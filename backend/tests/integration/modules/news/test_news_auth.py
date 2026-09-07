from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_news_endpoint_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            "/api/v1/news/assets/"
            f"{uuid4()}"
        
    )

    assert response.status_code == 401


def test_news_sync_endpoint_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        
            "/api/v1/news/assets/"
            f"{uuid4()}/sync"
        
    )

    assert response.status_code == 401


    