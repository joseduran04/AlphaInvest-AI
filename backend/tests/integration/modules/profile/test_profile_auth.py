from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_current_profile_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/profile/current"
    )

    assert response.status_code == 401


def test_profile_history_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/profile/history"
    )

    assert response.status_code == 401


def test_create_evaluation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/profile/evaluations",
        json={
            "questionnaire_id": str(uuid4()),
            "answers": [
                {
                    "question_id": str(uuid4()),
                    "option_id": str(uuid4()),
                }
            ],
        },
    )

    assert response.status_code == 401