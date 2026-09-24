import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from alphainvest.core.middleware import (
    RequestContextMiddleware,
    UnhandledErrorMiddleware,
)

pytestmark = pytest.mark.unit


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(UnhandledErrorMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/boom")
    async def boom() -> None:
        raise ValueError("fallo inesperado")

    return app


def test_unexpected_errors_keep_cors_headers() -> None:
    """Sin esto el navegador reporta 'No fue posible conectar con el servidor'."""

    client = TestClient(build_app(), raise_server_exceptions=False)

    response = client.post(
        "/boom",
        headers={"Origin": "http://127.0.0.1:8080"},
    )

    assert response.status_code == 500
    assert (
        response.headers["access-control-allow-origin"]
        == "http://127.0.0.1:8080"
    )
    assert response.json()["error"]["code"] == "internal_server_error"
