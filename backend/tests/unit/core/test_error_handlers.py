
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, model_validator

from alphainvest.core.error_handlers import (
    register_exception_handlers,
)

pytestmark = pytest.mark.unit


class UpdateRequest(BaseModel):
    value: int | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(
        self,
    ) -> "UpdateRequest":
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo"
            )

        return self


def build_test_client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.patch("/resource")
    async def update_resource(
        request: UpdateRequest,
    ) -> dict[str, int | None]:
        return {"value": request.value}

    return TestClient(
        app,
        raise_server_exceptions=False,
    )


def test_validation_error_is_json_serializable(
) -> None:
    client = build_test_client()

    response = client.patch(
        "/resource",
        json={},
    )

    assert response.status_code == 422
    assert response.headers[
        "content-type"
    ].startswith("application/json")

    payload = response.json()

    assert payload["success"] is False
    assert (
        payload["error"]["code"]
        == "validation_error"
    )
    assert (
        payload["error"]["message"]
        == "Los datos enviados no son válidos"
    )

    details = payload["error"]["details"]

    assert isinstance(details, list)
    assert details
    assert (
        "Debe enviar al menos un campo"
        in details[0]["msg"]
    )