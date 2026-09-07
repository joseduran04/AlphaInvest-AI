import csv
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from typing import cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    current_context,
)
from alphainvest.modules.auth.presentation.schemas import (
    UserResponse,
)

pytestmark = pytest.mark.integration


REPORT_ENDPOINTS = (
    "/api/v1/reports/assets",
    "/api/v1/reports/portfolios",
    "/api/v1/reports/simulations",
    "/api/v1/reports/recommendations",
    "/api/v1/reports/admin/users",
    "/api/v1/reports/admin/audit",
    "/api/v1/reports/admin/jobs",
    "/api/v1/reports/export/assets",
    "/api/v1/reports/export/portfolios",
    "/api/v1/reports/export/simulations",
    "/api/v1/reports/export/recommendations",
    "/api/v1/reports/admin/export/users",
    "/api/v1/reports/admin/export/audit",
    "/api/v1/reports/admin/export/jobs",
)


USER_REPORT_ENDPOINTS = (
    "/api/v1/reports/portfolios",
    "/api/v1/reports/simulations",
    "/api/v1/reports/recommendations",
)


ADMIN_REPORT_ENDPOINTS = (
    "/api/v1/reports/admin/users",
    "/api/v1/reports/admin/audit",
    "/api/v1/reports/admin/jobs",
)


ADMIN_EXPORT_ENDPOINTS = (
    "/api/v1/reports/admin/export/users",
    "/api/v1/reports/admin/export/audit",
    "/api/v1/reports/admin/export/jobs",
)


def _build_auth_context(
    *,
    permissions: list[str],
) -> AuthContext:
    user = UserResponse(
        id=uuid4(),
        nombres="Reporting",
        apellidos="Integration Test",
        correo="reporting-test@alphainvest.local",
        estado="ACTIVO",
        correo_verificado=True,
        roles=["TEST_REPORTING"],
        permisos=permissions,
    )

    return AuthContext(
        user=user,
        session_id=uuid4(),
    )


@contextmanager
def _authorized(
    client: TestClient,
    *,
    permissions: list[str],
) -> Iterator[AuthContext]:
    context = _build_auth_context(
        permissions=permissions,
    )

    async def override_current_context() -> AuthContext:
        return context

    app = cast(
        FastAPI,
        client.app,
    )

    app.dependency_overrides[
        current_context
    ] = override_current_context

    try:
        yield context
    finally:
        app.dependency_overrides.pop(
            current_context,
            None,
        )


def _assert_csv_response(
    response: object,
) -> None:
    assert hasattr(
        response,
        "status_code",
    )
    assert hasattr(
        response,
        "headers",
    )
    assert hasattr(
        response,
        "content",
    )

    status_code = response.status_code
    headers = response.headers
    content = response.content

    assert status_code == 200

    content_type = headers.get(
        "content-type",
        "",
    )
    assert content_type.startswith(
        "text/csv"
    )

    content_disposition = headers.get(
        "content-disposition",
        "",
    )
    assert "attachment" in content_disposition
    assert ".csv" in content_disposition

    assert content.startswith(
        b"\xef\xbb\xbf"
    )

    decoded = content.decode(
        "utf-8-sig"
    )

    reader = csv.reader(
        StringIO(decoded)
    )
    rows = list(reader)

    assert rows
    assert rows[0]


@pytest.mark.parametrize(
    "endpoint",
    REPORT_ENDPOINTS,
)
def test_reporting_endpoints_require_authentication(
    client: TestClient,
    endpoint: str,
) -> None:
    response = client.get(
        endpoint
    )

    assert response.status_code == 401


def test_reader_can_access_asset_report(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            "/api/v1/reports/assets"
        )

    assert response.status_code == 200

    payload = response.json()

    assert "items" in payload
    assert "total" in payload
    assert "limit" in payload
    assert "offset" in payload

    assert isinstance(
        payload["items"],
        list,
    )
    assert isinstance(
        payload["total"],
        int,
    )


@pytest.mark.parametrize(
    "endpoint",
    USER_REPORT_ENDPOINTS,
)
def test_user_reports_are_scoped_to_authenticated_user(
    client: TestClient,
    endpoint: str,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            endpoint,
            params={
                "limit": 100,
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["items"] == []
    assert payload["total"] == 0


def test_reader_cannot_export_without_export_permission(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            "/api/v1/reports/export/assets"
        )

    assert response.status_code == 403


def test_exporter_can_export_assets_csv(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.exportar",
        ],
    ):
        response = client.get(
            "/api/v1/reports/export/assets",
            params={
                "limit": 10,
            },
        )

    _assert_csv_response(
        response
    )

    decoded = response.content.decode(
        "utf-8-sig"
    )

    reader = csv.reader(
        StringIO(decoded)
    )
    header = next(reader)

    assert "asset_id" in header
    assert "symbol" in header


@pytest.mark.parametrize(
    "endpoint",
    (
        "/api/v1/reports/export/portfolios",
        "/api/v1/reports/export/simulations",
        "/api/v1/reports/export/recommendations",
    ),
)
def test_user_csv_exports_are_scoped_and_valid(
    client: TestClient,
    endpoint: str,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.exportar",
        ],
    ):
        response = client.get(
            endpoint,
            params={
                "limit": 10,
            },
        )

    _assert_csv_response(
        response
    )


@pytest.mark.parametrize(
    "endpoint",
    ADMIN_REPORT_ENDPOINTS,
)
def test_reader_cannot_access_admin_reports(
    client: TestClient,
    endpoint: str,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            endpoint
        )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "endpoint",
    ADMIN_REPORT_ENDPOINTS,
)
def test_admin_permission_can_access_admin_reports(
    client: TestClient,
    endpoint: str,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.administrar",
        ],
    ):
        response = client.get(
            endpoint,
            params={
                "limit": 10,
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert "items" in payload
    assert "total" in payload
    assert isinstance(
        payload["items"],
        list,
    )


@pytest.mark.parametrize(
    "endpoint",
    ADMIN_EXPORT_ENDPOINTS,
)
def test_admin_export_requires_export_permission_too(
    client: TestClient,
    endpoint: str,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.administrar",
        ],
    ):
        response = client.get(
            endpoint,
            params={
                "limit": 10,
            },
        )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "endpoint",
    ADMIN_EXPORT_ENDPOINTS,
)
def test_admin_with_both_permissions_can_export_csv(
    client: TestClient,
    endpoint: str,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.administrar",
            "reportes.exportar",
        ],
    ):
        response = client.get(
            endpoint,
            params={
                "limit": 10,
            },
        )

    _assert_csv_response(
        response
    )


def test_export_permission_does_not_grant_admin_access(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.exportar",
        ],
    ):
        response = client.get(
            "/api/v1/reports/admin/users"
        )

    assert response.status_code == 403


def test_read_permission_does_not_grant_export_access(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            "/api/v1/reports/export/assets"
        )

    assert response.status_code == 403


def test_asset_report_pagination_is_enforced(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            "/api/v1/reports/assets",
            params={
                "limit": 1,
                "offset": 0,
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["limit"] == 1
    assert payload["offset"] == 0
    assert len(payload["items"]) <= 1


def test_invalid_report_limit_is_rejected(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.leer",
        ],
    ):
        response = client.get(
            "/api/v1/reports/assets",
            params={
                "limit": 101,
            },
        )

    assert response.status_code == 422


def test_invalid_export_limit_is_rejected(
    client: TestClient,
) -> None:
    with _authorized(
        client,
        permissions=[
            "reportes.exportar",
        ],
    ):
        response = client.get(
            "/api/v1/reports/export/assets",
            params={
                "limit": 5001,
            },
        )

    assert response.status_code == 422