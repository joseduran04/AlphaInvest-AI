from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_create_configuration_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/simulations/configurations",
        json={
            "nombre": "Simulación prueba",
            "tipo_simulacion": "HISTORICA",
            "capital_inicial": "10000",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2025-01-01",
        },
    )

    assert response.status_code == 401


def test_list_configurations_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/simulations/configurations"
    )

    assert response.status_code == 401


def test_get_configuration_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            "/api/v1/simulations/configurations/"
            f"{uuid4()}"
        
    )

    assert response.status_code == 401


def test_update_configuration_requires_authentication(
    client: TestClient,
) -> None:
    response = client.patch(
        (
            "/api/v1/simulations/configurations/"
            f"{uuid4()}"
        ),
        json={
            "nombre": "Configuración actualizada",
        },
    )

    assert response.status_code == 401


def test_archive_configuration_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/archive"
        
    )

    assert response.status_code == 401


def test_add_configuration_asset_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        (
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/assets"
        ),
        json={
            "activo_id": str(uuid4()),
            "porcentaje_asignado": "50",
            "orden": 1,
        },
    )

    assert response.status_code == 401


def test_list_configuration_assets_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/assets"
        
    )

    assert response.status_code == 401


def test_update_configuration_asset_requires_authentication(
    client: TestClient,
) -> None:
    response = client.patch(
        (
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/assets/{uuid4()}"
        ),
        json={
            "porcentaje_asignado": "50",
        },
    )

    assert response.status_code == 401


def test_delete_configuration_asset_requires_authentication(
    client: TestClient,
) -> None:
    response = client.delete(
        
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/assets/{uuid4()}"
        
    )

    assert response.status_code == 401


def test_distribution_status_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/distribution"
        
    )

    assert response.status_code == 401


def test_mark_configuration_ready_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        
            "/api/v1/simulations/configurations/"
            f"{uuid4()}/ready"
        
    )

    assert response.status_code == 401


def test_create_execution_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/simulations/executions",
        json={
            "configuracion_id": str(uuid4()),
        },
    )

    assert response.status_code == 401


def test_list_executions_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/simulations/executions"
    )

    assert response.status_code == 401


def test_get_execution_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            "/api/v1/simulations/executions/"
            f"{uuid4()}"
        
    )

    assert response.status_code == 401


def test_get_execution_result_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        
            "/api/v1/simulations/executions/"
            f"{uuid4()}/result"
        
    )

    assert response.status_code == 401


def test_cancel_execution_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        
            "/api/v1/simulations/executions/"
            f"{uuid4()}/cancel"
        
    )

    assert response.status_code == 401