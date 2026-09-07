from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/ai/models",
        "/api/v1/ai/models/code/PREDICCION_TENDENCIA",
        (
            "/api/v1/ai/models/code/"
            "PREDICCION_TENDENCIA/active-version"
        ),
        f"/api/v1/ai/models/{uuid4()}",
        f"/api/v1/ai/models/{uuid4()}/versions",
        (
            f"/api/v1/ai/models/{uuid4()}"
            "/active-version"
        ),
        f"/api/v1/ai/versions/{uuid4()}",
    ],
)
def test_ai_endpoints_require_authentication(
    client: TestClient,
    path: str,
) -> None:
    response = client.get(path)

    assert response.status_code == 401


def test_ai_model_status_update_requires_authentication(
    client: TestClient,
) -> None:
    response = client.patch(
        f"/api/v1/ai/models/{uuid4()}/status",
        json={
            "status": "VALIDACION",
        },
    )

    assert response.status_code == 401


def test_ai_model_version_creation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/ai/models/{uuid4()}/versions",
        json={
            "version": "1.0.0",
            "artifact_path": "models/test/1.0.0",
            "checksum": "test-checksum",
            "algorithm": "XGBoost",
            "framework": "xgboost",
            "trained_at": (
                "2026-08-16T18:00:00-06:00"
            ),
        },
    )

    assert response.status_code == 401


def test_ai_model_version_activation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/ai/versions/{uuid4()}/activate"
    )

    assert response.status_code == 401


def test_ai_model_version_deactivation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/ai/versions/{uuid4()}/deactivate"
    )

    assert response.status_code == 401


def test_recommendation_creation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/ai/recommendation-requests",
        json={
            "asset_id": str(uuid4()),
            "prediction_request_id": str(
                uuid4()
            ),
            "reference_date": "2026-08-27",
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "path",
    [
        f"/api/v1/ai/recommendation-requests/{uuid4()}",
        (
            "/api/v1/ai/recommendation-requests/"
            f"{uuid4()}/result"
        ),
    ],
)
def test_recommendation_read_requires_authentication(
    client: TestClient,
    path: str,
) -> None:
    response = client.get(path)

    assert response.status_code == 401


def test_integral_creation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/ai/integral-analysis-requests",
        json={
            "asset_id": str(uuid4()),
            "prediction_request_id": str(
                uuid4()
            ),
            "sentiment_request_ids": [],
            "reference_date": "2026-08-29",
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "path",
    [
        (
            "/api/v1/ai/"
            "integral-analysis-requests/"
            f"{uuid4()}"
        ),
        (
            "/api/v1/ai/"
            "integral-analysis-requests/"
            f"{uuid4()}/result"
        ),
    ],
)
def test_integral_read_requires_authentication(
    client: TestClient,
    path: str,
) -> None:
    response = client.get(path)

    assert response.status_code == 401