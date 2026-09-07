from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
    SimulationType,
)
from alphainvest.modules.simulation.presentation.schemas import (
    SimulationConfigurationAssetCreateRequest,
    SimulationConfigurationAssetUpdateRequest,
    SimulationConfigurationCreateRequest,
    SimulationConfigurationUpdateRequest,
    SimulationExecutionCancelResponse,
    SimulationExecutionCreateRequest,
    SimulationExecutionListResponse,
    SimulationExecutionResponse,
)

pytestmark = pytest.mark.unit


def build_create_request(
    **overrides: object,
) -> SimulationConfigurationCreateRequest:
    data: dict[str, object] = {
        "nombre": "Simulación histórica",
        "tipo_simulacion": "HISTORICA",
        "capital_inicial": Decimal("10000"),
        "moneda_base": "usd",
        "fecha_inicio": date(2024, 1, 1),
        "fecha_fin": date(2025, 1, 1),
    }
    data.update(overrides)

    return SimulationConfigurationCreateRequest(
        **data
    )


def test_create_configuration_accepts_valid_data(
) -> None:
    request = build_create_request()

    assert (
        request.tipo_simulacion
        == SimulationType.HISTORICAL
    )
    assert request.moneda_base == "USD"
    assert (
        request.aportacion_periodica
        == Decimal("0")
    )
    assert request.frecuencia_aportacion is None
    assert request.numero_escenarios == 1


def test_create_configuration_trims_text() -> None:
    request = build_create_request(
        nombre="  Simulación principal  ",
        descripcion="  Prueba histórica  ",
    )

    assert request.nombre == "Simulación principal"
    assert request.descripcion == "Prueba histórica"


def test_create_rejects_invalid_dates() -> None:
    with pytest.raises(
        ValidationError,
        match="fecha final",
    ):
        build_create_request(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 1),
        )


def test_create_requires_contribution_frequency(
) -> None:
    with pytest.raises(
        ValidationError,
        match="frecuencia",
    ):
        build_create_request(
            aportacion_periodica=Decimal("100"),
        )


def test_create_rejects_frequency_without_contribution(
) -> None:
    with pytest.raises(
        ValidationError,
        match="aportación es cero",
    ):
        build_create_request(
            frecuencia_aportacion="MENSUAL",
        )


def test_create_accepts_periodic_contribution(
) -> None:
    request = build_create_request(
        aportacion_periodica=Decimal("100"),
        frecuencia_aportacion="MENSUAL",
    )

    assert (
        request.frecuencia_aportacion
        == ContributionFrequency.MONTHLY
    )


def test_monte_carlo_requires_multiple_scenarios(
) -> None:
    with pytest.raises(
        ValidationError,
        match="Monte Carlo",
    ):
        build_create_request(
            tipo_simulacion="MONTE_CARLO",
            numero_escenarios=1,
        )


def test_monte_carlo_accepts_multiple_scenarios(
) -> None:
    request = build_create_request(
        tipo_simulacion="MONTE_CARLO",
        numero_escenarios=1000,
    )

    assert (
        request.tipo_simulacion
        == SimulationType.MONTE_CARLO
    )
    assert request.numero_escenarios == 1000


def test_update_rejects_empty_request() -> None:
    with pytest.raises(
        ValidationError,
        match="Debe enviar al menos un campo",
    ):
        SimulationConfigurationUpdateRequest()


def test_update_normalizes_currency() -> None:
    request = (
        SimulationConfigurationUpdateRequest(
            moneda_base="mxn"
        )
    )

    assert request.moneda_base == "MXN"


def test_update_allows_nullable_description() -> None:
    request = (
        SimulationConfigurationUpdateRequest(
            descripcion=None
        )
    )

    assert "descripcion" in request.model_fields_set
    assert request.descripcion is None


def test_create_rejects_non_positive_capital() -> None:
    with pytest.raises(ValidationError):
        build_create_request(
            capital_inicial=Decimal("0")
        )


def test_create_rejects_short_currency() -> None:
    with pytest.raises(
        ValidationError,
        match="at least 3 characters",
    ):
        build_create_request(
            moneda_base="US"
        )


def test_create_rejects_non_alphabetic_currency(
) -> None:
    with pytest.raises(
        ValidationError,
        match="tres letras",
    ):
        build_create_request(
            moneda_base="U1D"
        )


def test_configuration_asset_accepts_valid_data(
) -> None:
    asset_id = uuid4()

    request = (
        SimulationConfigurationAssetCreateRequest(
            activo_id=asset_id,
            porcentaje_asignado=Decimal("60"),
            monto_inicial=Decimal("6000"),
            precio_inicial=Decimal("150"),
            orden=1,
            parametros={
                "rebalanceo": True,
            },
        )
    )

    assert request.activo_id == asset_id
    assert (
        request.porcentaje_asignado
        == Decimal("60")
    )
    assert request.orden == 1


def test_configuration_asset_rejects_zero_percentage(
) -> None:
    with pytest.raises(ValidationError):
        SimulationConfigurationAssetCreateRequest(
            activo_id=uuid4(),
            porcentaje_asignado=Decimal("0"),
            orden=1,
        )


def test_configuration_asset_rejects_percentage_above_100(
) -> None:
    with pytest.raises(ValidationError):
        SimulationConfigurationAssetCreateRequest(
            activo_id=uuid4(),
            porcentaje_asignado=Decimal("100.01"),
            orden=1,
        )


def test_configuration_asset_rejects_invalid_order(
) -> None:
    with pytest.raises(ValidationError):
        SimulationConfigurationAssetCreateRequest(
            activo_id=uuid4(),
            porcentaje_asignado=Decimal("50"),
            orden=0,
        )


def test_configuration_asset_allows_optional_values(
) -> None:
    request = (
        SimulationConfigurationAssetCreateRequest(
            activo_id=uuid4(),
            porcentaje_asignado=Decimal("50"),
            orden=1,
        )
    )

    assert request.monto_inicial is None
    assert request.precio_inicial is None
    assert request.parametros is None


def test_configuration_asset_update_rejects_empty_request(
) -> None:
    with pytest.raises(
        ValidationError,
        match="Debe enviar al menos un campo",
    ):
        SimulationConfigurationAssetUpdateRequest()


def test_configuration_asset_update_allows_null_fields(
) -> None:
    request = (
        SimulationConfigurationAssetUpdateRequest(
            monto_inicial=None,
            precio_inicial=None,
            parametros=None,
        )
    )

    assert "monto_inicial" in request.model_fields_set
    assert "precio_inicial" in request.model_fields_set
    assert "parametros" in request.model_fields_set


def test_execution_create_accepts_configuration(
) -> None:
    configuration_id = uuid4()

    request = SimulationExecutionCreateRequest(
        configuracion_id=configuration_id,
        parametros_ejecucion={
            "origen": "VALIDACION_11_4",
        },
    )

    assert (
        request.configuracion_id
        == configuration_id
    )
    assert request.version_modelo_id is None
    assert request.parametros_ejecucion == {
        "origen": "VALIDACION_11_4",
    }


def test_execution_create_accepts_model_version(
) -> None:
    model_version_id = uuid4()

    request = SimulationExecutionCreateRequest(
        configuracion_id=uuid4(),
        version_modelo_id=model_version_id,
    )

    assert (
        request.version_modelo_id
        == model_version_id
    )


def test_execution_response_accepts_pending_state(
) -> None:
    now = datetime.now(UTC)

    response = SimulationExecutionResponse(
        id=uuid4(),
        configuracion_id=uuid4(),
        usuario_id=uuid4(),
        version_modelo_id=None,
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=now,
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        parametros_ejecucion=None,
        identificador_proceso=None,
    )

    assert response.estado.value == "PENDIENTE"
    assert (
        response.porcentaje_progreso
        == Decimal("0")
    )


def test_execution_list_accepts_filters(
) -> None:
    configuration_id = uuid4()

    response = SimulationExecutionListResponse(
        items=[],
        total=0,
        limit=50,
        offset=0,
        estado="EJECUTANDO",
        configuracion_id=configuration_id,
    )

    assert response.total == 0
    assert response.estado is not None
    assert response.estado.value == "EJECUTANDO"
    assert (
        response.configuracion_id
        == configuration_id
    )


def test_execution_cancel_response_requires_end_date(
) -> None:
    now = datetime.now(UTC)

    response = SimulationExecutionCancelResponse(
        id=uuid4(),
        estado="CANCELADA",
        porcentaje_progreso=Decimal("0"),
        fecha_inicio=now,
        fecha_fin=now,
    )

    assert response.estado.value == "CANCELADA"
    assert response.fecha_fin == now