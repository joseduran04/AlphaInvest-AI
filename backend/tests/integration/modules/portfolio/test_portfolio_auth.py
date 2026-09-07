from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_create_portfolio_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/portfolios",
        json={
            "nombre": "Portafolio prueba",
            "moneda_base": "USD",
            "capital_inicial": "10000",
            "tipo": "VIRTUAL",
        },
    )

    assert response.status_code == 401


def test_list_portfolios_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/portfolios"
    )

    assert response.status_code == 401


def test_get_portfolio_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        f"/api/v1/portfolios/{uuid4()}"
    )

    assert response.status_code == 401


def test_create_position_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/portfolios/{uuid4()}/positions",
        json={
            "activo_id": str(uuid4()),
            "cantidad": "10",
            "precio_promedio_compra": "100",
        },
    )

    assert response.status_code == 401


def test_list_positions_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        f"/api/v1/portfolios/{uuid4()}/positions"
    )

    assert response.status_code == 401


def test_update_position_requires_authentication(
    client: TestClient,
) -> None:
    response = client.patch(
        (
            f"/api/v1/portfolios/{uuid4()}"
            f"/positions/{uuid4()}"
        ),
        json={
            "cantidad": "15",
        },
    )

    assert response.status_code == 401


def test_delete_position_requires_authentication(
    client: TestClient,
) -> None:
    response = client.delete(
        
            f"/api/v1/portfolios/{uuid4()}"
            f"/positions/{uuid4()}"
        
    )

    assert response.status_code == 401


def test_portfolio_summary_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            f"/api/v1/portfolios/{uuid4()}"
            "/summary"
        
    )

    assert response.status_code == 401


def test_asset_allocation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            f"/api/v1/portfolios/{uuid4()}"
            "/allocation/assets"
        
    )

    assert response.status_code == 401


def test_sector_allocation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            f"/api/v1/portfolios/{uuid4()}"
            "/allocation/sectors"
        
    )

    assert response.status_code == 401


def test_register_valuation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        (
            f"/api/v1/portfolios/{uuid4()}"
            "/valuations"
        ),
        json={},
    )

    assert response.status_code == 401


def test_list_valuations_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            f"/api/v1/portfolios/{uuid4()}"
            "/valuations"
        
    )

    assert response.status_code == 401


