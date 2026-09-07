from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.application.service import (
    SimulationService,
)
from alphainvest.modules.simulation.domain.enums import (
    SimulationConfigurationStatus,
)
from alphainvest.modules.simulation.domain.exceptions import (
    SimulationAssetNotFoundError,
    SimulationAssetUnavailableError,
    SimulationConfigurationAssetAlreadyExistsError,
    SimulationConfigurationAssetNotFoundError,
    SimulationConfigurationNameAlreadyExistsError,
    SimulationConfigurationNotFoundError,
    SimulationConfigurationUnavailableError,
    SimulationDistributionInvalidError,
    SimulationExecutionAlreadyActiveError,
    SimulationExecutionNotFoundError,
    SimulationExecutionUnavailableError,
    SimulationModelVersionNotFoundError,
    SimulationModelVersionUnavailableError,
    SimulationPortfolioNotFoundError,
)
from alphainvest.modules.simulation.presentation.schemas import (
    SimulationConfigurationAssetCreateRequest,
    SimulationConfigurationAssetUpdateRequest,
    SimulationConfigurationCreateRequest,
    SimulationConfigurationUpdateRequest,
    SimulationExecutionCreateRequest,
    SimulationExecutionStatus,
)

pytestmark = pytest.mark.unit


def build_configuration(
    *,
    status: str = "BORRADOR",
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        portafolio_id=None,
        nombre="Simulación histórica",
        descripcion=None,
        tipo_simulacion="HISTORICA",
        capital_inicial=Decimal("10000"),
        moneda_base="USD",
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2025, 1, 1),
        aportacion_periodica=Decimal("0"),
        frecuencia_aportacion=None,
        comision_porcentaje=Decimal("0"),
        inflacion_anual=None,
        tasa_libre_riesgo=None,
        numero_escenarios=1,
        semilla_aleatoria=None,
        parametros=None,
        estado=status,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )


def build_configuration_asset(
    *,
    configuration_id=None,
    asset_id=None,
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        configuracion_id=(
            configuration_id or uuid4()
        ),
        activo_id=asset_id or uuid4(),
        porcentaje_asignado=Decimal("60"),
        monto_inicial=Decimal("6000"),
        precio_inicial=Decimal("150"),
        orden=1,
        parametros=None,
        fecha_agregado=now,
    )


def build_distribution_data(
    *,
    configuration_id,
    status: str = "BORRADOR",
    valid: bool = True,
) -> dict[str, object]:
    return {
        "configuracion_id": configuration_id,
        "estado": status,
        "capital_inicial": Decimal("10000"),
        "cantidad_activos": 2,
        "porcentaje_total": Decimal(
            "100" if valid else "60"
        ),
        "monto_total": Decimal("10000"),
        "distribucion_valida": valid,
    }


def build_service(
    *,
    repository: SimpleNamespace,
    portfolio_repository: (
        SimpleNamespace | None
    ) = None,
    market_repository: (
        SimpleNamespace | None
    ) = None,
    ai_repository: (
        SimpleNamespace | None
    ) = None,
) -> SimulationService:
    if portfolio_repository is None:
        portfolio_repository = SimpleNamespace(
            get_by_id_for_user=AsyncMock(
                return_value=None
            )
        )

    if market_repository is None:
        market_repository = SimpleNamespace(
            get_asset=AsyncMock(
                return_value=None
            )
        )

    if ai_repository is None:
        ai_repository = SimpleNamespace(
            get_model_version=AsyncMock(
                return_value=None
            ),
            get_active_model_version=AsyncMock(
                return_value=None
            ),
        )

    return SimulationService(
        repository=repository,
        portfolio_repository=portfolio_repository,
        market_repository=market_repository,
        ai_repository=ai_repository,
    )


def build_execution(
    *,
    status: str = "PENDIENTE",
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        configuracion_id=uuid4(),
        usuario_id=uuid4(),
        version_modelo_id=None,
        estado=status,
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=now,
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        parametros_ejecucion=None,
        identificador_proceso=None,
    )


def build_asset_result(
    *,
    result_id,
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        resultado_id=result_id,
        activo_id=uuid4(),
        porcentaje_asignado=Decimal("100"),
        capital_asignado=Decimal("10000"),
        cantidad_inicial=Decimal("100"),
        precio_inicial=Decimal("100"),
        precio_final=Decimal("110"),
        valor_final=Decimal("11000"),
        ganancia_perdida=Decimal("1000"),
        rendimiento_porcentaje=Decimal("10"),
        volatilidad=Decimal("15"),
        maximo_drawdown_porcentaje=(
            Decimal("5")
        ),
        detalle={
            "cantidad_final": "100",
        },
        fecha_registro=now,
    )


def build_result(
    *,
    execution_id,
) -> SimpleNamespace:
    now = datetime.now(UTC)
    result_id = uuid4()

    asset_result = build_asset_result(
        result_id=result_id
    )

    return SimpleNamespace(
        id=result_id,
        ejecucion_id=execution_id,
        capital_inicial=Decimal("10000"),
        aportaciones_totales=Decimal("0"),
        capital_final=Decimal("11000"),
        ganancia_perdida=Decimal("1000"),
        rendimiento_total_porcentaje=(
            Decimal("10")
        ),
        rendimiento_anualizado_porcentaje=(
            Decimal("10")
        ),
        volatilidad_anualizada=Decimal("15"),
        indice_sharpe=Decimal("0.40"),
        maximo_drawdown_porcentaje=(
            Decimal("5")
        ),
        valor_en_riesgo=Decimal("300"),
        nivel_confianza_var=Decimal("0.95"),
        mejor_escenario=None,
        peor_escenario=None,
        mediana_escenarios=None,
        probabilidad_ganancia=None,
        moneda="USD",
        resumen={
            "tipo": "HISTORICA",
        },
        fecha_registro=now,
        activos=[
            asset_result,
        ],
    )


@pytest.mark.asyncio
async def test_create_configuration() -> None:
    configuration = build_configuration()

    repository = SimpleNamespace(
        get_configuration_by_name_for_user=(
            AsyncMock(return_value=None)
        ),
        create_configuration=AsyncMock(
            return_value=configuration
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    request = SimulationConfigurationCreateRequest(
        nombre="Simulación histórica",
        tipo_simulacion="HISTORICA",
        capital_inicial=Decimal("10000"),
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2025, 1, 1),
    )

    response = await service.create_configuration(
        user_id=configuration.usuario_id,
        request=request,
    )

    assert response.id == configuration.id
    assert (
        response.estado
        == SimulationConfigurationStatus.DRAFT
    )
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_rejects_duplicate_name(
) -> None:
    repository = SimpleNamespace(
        get_configuration_by_name_for_user=(
            AsyncMock(
                return_value=build_configuration()
            )
        )
    )

    service = build_service(
        repository=repository
    )

    request = SimulationConfigurationCreateRequest(
        nombre="Simulación histórica",
        tipo_simulacion="HISTORICA",
        capital_inicial=Decimal("10000"),
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2025, 1, 1),
    )

    with pytest.raises(
        SimulationConfigurationNameAlreadyExistsError
    ):
        await service.create_configuration(
            user_id=uuid4(),
            request=request,
        )


@pytest.mark.asyncio
async def test_create_rejects_missing_portfolio(
) -> None:
    repository = SimpleNamespace(
        get_configuration_by_name_for_user=(
            AsyncMock(return_value=None)
        )
    )
    portfolio_repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=None
        )
    )

    service = build_service(
        repository=repository,
        portfolio_repository=portfolio_repository,
    )

    request = SimulationConfigurationCreateRequest(
        portafolio_id=uuid4(),
        nombre="Simulación histórica",
        tipo_simulacion="HISTORICA",
        capital_inicial=Decimal("10000"),
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2025, 1, 1),
    )

    with pytest.raises(
        SimulationPortfolioNotFoundError
    ):
        await service.create_configuration(
            user_id=uuid4(),
            request=request,
        )


@pytest.mark.asyncio
async def test_list_configurations() -> None:
    configuration = build_configuration()

    repository = SimpleNamespace(
        list_configurations_for_user=AsyncMock(
            return_value=([configuration], 1)
        )
    )

    service = build_service(
        repository=repository
    )

    response = await service.list_configurations(
        user_id=configuration.usuario_id,
        status=(
            SimulationConfigurationStatus.DRAFT
        ),
        limit=50,
        offset=0,
    )

    assert response.total == 1
    assert response.items[0].id == configuration.id
    assert (
        response.estado
        == SimulationConfigurationStatus.DRAFT
    )


@pytest.mark.asyncio
async def test_get_configuration_rejects_missing(
) -> None:
    repository = SimpleNamespace(
        get_configuration_by_id_for_user=(
            AsyncMock(return_value=None)
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationConfigurationNotFoundError
    ):
        await service.get_configuration(
            configuration_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_update_configuration() -> None:
    configuration = build_configuration()
    updated = build_configuration()
    updated.id = configuration.id
    updated.usuario_id = configuration.usuario_id
    updated.nombre = "Simulación actualizada"

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=(
            AsyncMock(
                return_value=configuration
            )
        ),
        get_configuration_by_name_for_user=(
            AsyncMock(return_value=None)
        ),
        update_configuration=AsyncMock(
            return_value=updated
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    response = await service.update_configuration(
        configuration_id=configuration.id,
        user_id=configuration.usuario_id,
        request=(
            SimulationConfigurationUpdateRequest(
                nombre="Simulación actualizada"
            )
        ),
    )

    assert (
        response.nombre
        == "Simulación actualizada"
    )
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_rejects_non_draft(
) -> None:
    configuration = build_configuration(
        status="LISTA"
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=(
            AsyncMock(
                return_value=configuration
            )
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationConfigurationUnavailableError
    ):
        await service.update_configuration(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationUpdateRequest(
                    nombre="Cambio"
                )
            ),
        )


@pytest.mark.asyncio
async def test_update_validates_final_dates(
) -> None:
    configuration = build_configuration()

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=(
            AsyncMock(
                return_value=configuration
            )
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        ValueError,
        match="fecha final",
    ):
        await service.update_configuration(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationUpdateRequest(
                    fecha_inicio=date(2026, 1, 1)
                )
            ),
        )


@pytest.mark.asyncio
async def test_archive_configuration() -> None:
    configuration = build_configuration()
    archived = build_configuration(
        status="ARCHIVADA"
    )
    archived.id = configuration.id

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=(
            AsyncMock(
                return_value=configuration
            )
        ),
        archive_configuration=AsyncMock(
            return_value=archived
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    response = await service.archive_configuration(
        configuration_id=configuration.id,
        user_id=configuration.usuario_id,
    )

    assert (
        response.estado
        == SimulationConfigurationStatus.ARCHIVED
    )
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_rejects_archived_configuration(
) -> None:
    configuration = build_configuration(
        status="ARCHIVADA"
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=(
            AsyncMock(
                return_value=configuration
            )
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationConfigurationUnavailableError
    ):
        await service.archive_configuration(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
        )

@pytest.mark.asyncio
async def test_add_configuration_asset() -> None:
    configuration = build_configuration()
    configuration_asset = (
        build_configuration_asset(
            configuration_id=configuration.id
        )
    )
    asset = SimpleNamespace(
        id=configuration_asset.activo_id,
        estado="ACTIVO",
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_configuration_asset=AsyncMock(
            return_value=None
        ),
        get_configuration_asset_by_order=AsyncMock(
            return_value=None
        ),
        create_configuration_asset=AsyncMock(
            return_value=configuration_asset
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    service = build_service(
        repository=repository,
        market_repository=market_repository,
    )

    response = await service.add_configuration_asset(
        configuration_id=configuration.id,
        user_id=configuration.usuario_id,
        request=(
            SimulationConfigurationAssetCreateRequest(
                activo_id=asset.id,
                porcentaje_asignado=Decimal("60"),
                monto_inicial=Decimal("6000"),
                precio_inicial=Decimal("150"),
                orden=1,
            )
        ),
    )

    assert response.activo_id == asset.id
    assert response.orden == 1
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_asset_rejects_missing_asset(
) -> None:
    configuration = build_configuration()

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        )
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=None
        )
    )

    service = build_service(
        repository=repository,
        market_repository=market_repository,
    )

    with pytest.raises(
        SimulationAssetNotFoundError
    ):
        await service.add_configuration_asset(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationAssetCreateRequest(
                    activo_id=uuid4(),
                    porcentaje_asignado=Decimal("60"),
                    orden=1,
                )
            ),
        )


@pytest.mark.asyncio
async def test_add_asset_rejects_inactive_asset(
) -> None:
    configuration = build_configuration()
    asset = SimpleNamespace(
        id=uuid4(),
        estado="INACTIVO",
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        )
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    service = build_service(
        repository=repository,
        market_repository=market_repository,
    )

    with pytest.raises(
        SimulationAssetUnavailableError
    ):
        await service.add_configuration_asset(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationAssetCreateRequest(
                    activo_id=asset.id,
                    porcentaje_asignado=Decimal("60"),
                    orden=1,
                )
            ),
        )


@pytest.mark.asyncio
async def test_add_asset_rejects_duplicate_asset(
) -> None:
    configuration = build_configuration()
    configuration_asset = (
        build_configuration_asset(
            configuration_id=configuration.id
        )
    )
    asset = SimpleNamespace(
        id=configuration_asset.activo_id,
        estado="ACTIVO",
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_configuration_asset=AsyncMock(
            return_value=configuration_asset
        ),
    )
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    service = build_service(
        repository=repository,
        market_repository=market_repository,
    )

    with pytest.raises(
        SimulationConfigurationAssetAlreadyExistsError
    ):
        await service.add_configuration_asset(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationAssetCreateRequest(
                    activo_id=asset.id,
                    porcentaje_asignado=Decimal("60"),
                    orden=1,
                )
            ),
        )


@pytest.mark.asyncio
async def test_list_configuration_assets(
) -> None:
    configuration = build_configuration()
    configuration_asset = (
        build_configuration_asset(
            configuration_id=configuration.id
        )
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        list_configuration_assets=AsyncMock(
            return_value=[configuration_asset]
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id
            )
        ),
    )

    service = build_service(
        repository=repository
    )

    response = await service.list_configuration_assets(
        configuration_id=configuration.id,
        user_id=configuration.usuario_id,
    )

    assert response.total == 1
    assert response.porcentaje_total == Decimal(
        "100"
    )
    assert response.distribucion_valida is True


@pytest.mark.asyncio
async def test_update_configuration_asset(
) -> None:
    configuration = build_configuration()
    configuration_asset = (
        build_configuration_asset(
            configuration_id=configuration.id
        )
    )
    updated = build_configuration_asset(
        configuration_id=configuration.id,
        asset_id=configuration_asset.activo_id,
    )
    updated.porcentaje_asignado = Decimal("50")
    updated.orden = 2

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_configuration_asset=AsyncMock(
            return_value=configuration_asset
        ),
        get_configuration_asset_by_order=AsyncMock(
            return_value=None
        ),
        update_configuration_asset=AsyncMock(
            return_value=updated
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    response = (
        await service.update_configuration_asset(
            configuration_id=configuration.id,
            asset_id=configuration_asset.activo_id,
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationAssetUpdateRequest(
                    porcentaje_asignado=Decimal("50"),
                    orden=2,
                )
            ),
        )
    )

    assert (
        response.porcentaje_asignado
        == Decimal("50")
    )
    assert response.orden == 2
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_rejects_missing_configuration_asset(
) -> None:
    configuration = build_configuration()

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_configuration_asset=AsyncMock(
            return_value=None
        ),
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationConfigurationAssetNotFoundError
    ):
        await service.update_configuration_asset(
            configuration_id=configuration.id,
            asset_id=uuid4(),
            user_id=configuration.usuario_id,
            request=(
                SimulationConfigurationAssetUpdateRequest(
                    porcentaje_asignado=Decimal("50")
                )
            ),
        )


@pytest.mark.asyncio
async def test_delete_configuration_asset(
) -> None:
    configuration = build_configuration()
    configuration_asset = (
        build_configuration_asset(
            configuration_id=configuration.id
        )
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_configuration_asset=AsyncMock(
            return_value=configuration_asset
        ),
        delete_configuration_asset=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    await service.delete_configuration_asset(
        configuration_id=configuration.id,
        asset_id=configuration_asset.activo_id,
        user_id=configuration.usuario_id,
    )

    repository.delete_configuration_asset.assert_awaited_once_with(
        configuration_asset
    )
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_configuration_ready(
) -> None:
    configuration = build_configuration()
    ready = build_configuration(
        status="LISTA"
    )
    ready.id = configuration.id

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            side_effect=[
                build_distribution_data(
                    configuration_id=configuration.id
                ),
                build_distribution_data(
                    configuration_id=configuration.id,
                    status="LISTA",
                ),
            ]
        ),
        mark_configuration_ready=AsyncMock(
            return_value=ready
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    response = await service.mark_configuration_ready(
        configuration_id=configuration.id,
        user_id=configuration.usuario_id,
    )

    assert (
        response.estado
        == SimulationConfigurationStatus.READY
    )
    assert response.distribucion.distribucion_valida
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_ready_rejects_invalid_distribution(
) -> None:
    configuration = build_configuration()

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id,
                valid=False,
            )
        ),
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationDistributionInvalidError
    ):
        await service.mark_configuration_ready(
            configuration_id=configuration.id,
            user_id=configuration.usuario_id,
        )


@pytest.mark.asyncio
async def test_create_execution() -> None:
    configuration = build_configuration(
        status="LISTA"
    )
    execution = build_execution()
    execution.configuracion_id = configuration.id
    execution.usuario_id = configuration.usuario_id

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id,
                status="LISTA",
            )
        ),
        get_active_execution_for_configuration=(
            AsyncMock(return_value=None)
        ),
        create_execution=AsyncMock(
            return_value=execution
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    response = await service.create_execution(
        user_id=configuration.usuario_id,
        request=SimulationExecutionCreateRequest(
            configuracion_id=configuration.id,
            parametros_ejecucion={
                "origen": "TEST",
            },
        ),
    )

    assert response.id == execution.id
    assert response.estado.value == "PENDIENTE"
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_execution_rejects_non_ready_configuration(
) -> None:
    configuration = build_configuration(
        status="BORRADOR"
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationConfigurationUnavailableError
    ):
        await service.create_execution(
            user_id=configuration.usuario_id,
            request=SimulationExecutionCreateRequest(
                configuracion_id=configuration.id
            ),
        )


@pytest.mark.asyncio
async def test_create_execution_rejects_invalid_distribution(
) -> None:
    configuration = build_configuration(
        status="LISTA"
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id,
                status="LISTA",
                valid=False,
            )
        ),
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationDistributionInvalidError
    ):
        await service.create_execution(
            user_id=configuration.usuario_id,
            request=SimulationExecutionCreateRequest(
                configuracion_id=configuration.id
            ),
        )


@pytest.mark.asyncio
async def test_create_execution_rejects_active_execution(
) -> None:
    configuration = build_configuration(
        status="LISTA"
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id,
                status="LISTA",
            )
        ),
        get_active_execution_for_configuration=(
            AsyncMock(
                return_value=build_execution()
            )
        ),
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationExecutionAlreadyActiveError
    ):
        await service.create_execution(
            user_id=configuration.usuario_id,
            request=SimulationExecutionCreateRequest(
                configuracion_id=configuration.id
            ),
        )


@pytest.mark.asyncio
async def test_create_execution_rejects_missing_model_version(
) -> None:
    configuration = build_configuration(
        status="LISTA"
    )
    version_id = uuid4()

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id,
                status="LISTA",
            )
        ),
        get_active_execution_for_configuration=(
            AsyncMock(return_value=None)
        ),
    )
    ai_repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=None
        ),
        get_active_model_version=AsyncMock(
            return_value=None
        ),
    )

    service = build_service(
        repository=repository,
        ai_repository=ai_repository,
    )

    with pytest.raises(
        SimulationModelVersionNotFoundError
    ):
        await service.create_execution(
            user_id=configuration.usuario_id,
            request=SimulationExecutionCreateRequest(
                configuracion_id=configuration.id,
                version_modelo_id=version_id,
            ),
        ) 


@pytest.mark.asyncio
async def test_create_execution_rejects_inactive_model_version(
) -> None:
    configuration = build_configuration(
        status="LISTA"
    )
    version = SimpleNamespace(
        id=uuid4(),
        activa=False,
    )

    repository = SimpleNamespace(
        get_configuration_by_id_for_user=AsyncMock(
            return_value=configuration
        ),
        get_distribution_status=AsyncMock(
            return_value=build_distribution_data(
                configuration_id=configuration.id,
                status="LISTA",
            )
        ),
        get_active_execution_for_configuration=(
            AsyncMock(return_value=None)
        ),
    )
    ai_repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=version
        ),
        get_active_model_version=AsyncMock(
            return_value=None
        ),
    )

    service = build_service(
        repository=repository,
        ai_repository=ai_repository,
    )

    with pytest.raises(
        SimulationModelVersionUnavailableError
    ):
        await service.create_execution(
            user_id=configuration.usuario_id,
            request=SimulationExecutionCreateRequest(
                configuracion_id=configuration.id,
                version_modelo_id=version.id,
            ),
        )


@pytest.mark.asyncio
async def test_list_executions() -> None:
    execution = build_execution()

    repository = SimpleNamespace(
        list_executions_for_user=AsyncMock(
            return_value=([execution], 1)
        )
    )

    service = build_service(
        repository=repository
    )

    response = await service.list_executions(
        user_id=execution.usuario_id,
        status=SimulationExecutionStatus(
            "PENDIENTE"
        ),
        configuration_id=None,
        limit=50,
        offset=0,
    )

    assert response.total == 1
    assert response.items[0].id == execution.id
    assert response.estado is not None
    assert response.estado.value == "PENDIENTE"


@pytest.mark.asyncio
async def test_get_execution_rejects_missing(
) -> None:
    repository = SimpleNamespace(
        get_execution_by_id_for_user=AsyncMock(
            return_value=None
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationExecutionNotFoundError
    ):
        await service.get_execution(
            execution_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_result() -> None:
    execution = build_execution(
        status="COMPLETADA"
    )

    result = build_result(
        execution_id=execution.id
    )

    execution.resultado = result

    repository = SimpleNamespace(
        get_execution_by_id_for_user=AsyncMock(
            return_value=execution
        )
    )

    service = build_service(
        repository=repository
    )

    response = await service.get_result(
        execution_id=execution.id,
        user_id=execution.usuario_id,
    )

    assert response.id == result.id

    assert (
        response.ejecucion_id
        == execution.id
    )

    assert (
        response.capital_inicial
        == Decimal("10000")
    )

    assert (
        response.capital_final
        == Decimal("11000")
    )

    assert (
        response.ganancia_perdida
        == Decimal("1000")
    )

    assert (
        response.rendimiento_total_porcentaje
        == Decimal("10")
    )

    assert response.moneda == "USD"

    assert len(response.activos) == 1

    assert (
        response.activos[0].activo_id
        == result.activos[0].activo_id
    )

    assert (
        response.activos[0].valor_final
        == Decimal("11000")
    )

    repository.get_execution_by_id_for_user.assert_awaited_once_with(
        execution_id=execution.id,
        user_id=execution.usuario_id,
    )


@pytest.mark.asyncio
async def test_get_result_rejects_missing_result(
) -> None:
    execution = build_execution(
        status="EJECUTANDO"
    )
    execution.resultado = None

    repository = SimpleNamespace(
        get_execution_by_id_for_user=AsyncMock(
            return_value=execution
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationExecutionUnavailableError,
        match="todavía no tiene",
    ):
        await service.get_result(
            execution_id=execution.id,
            user_id=execution.usuario_id,
        )


@pytest.mark.asyncio
async def test_cancel_execution() -> None:
    execution = build_execution()
    cancelled = build_execution(
        status="CANCELADA"
    )
    cancelled.id = execution.id
    cancelled.usuario_id = execution.usuario_id

    now = datetime.now(UTC)
    cancelled.fecha_inicio = now
    cancelled.fecha_fin = now

    repository = SimpleNamespace(
        get_execution_by_id_for_user=AsyncMock(
            return_value=execution
        ),
        cancel_execution=AsyncMock(
            return_value=cancelled
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = build_service(
        repository=repository
    )

    response = await service.cancel_execution(
        execution_id=execution.id,
        user_id=execution.usuario_id,
    )

    assert response.id == execution.id
    assert response.estado.value == "CANCELADA"
    assert response.fecha_fin == now
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_execution_rejects_terminal_state(
) -> None:
    execution = build_execution(
        status="COMPLETADA"
    )

    repository = SimpleNamespace(
        get_execution_by_id_for_user=AsyncMock(
            return_value=execution
        )
    )

    service = build_service(
        repository=repository
    )

    with pytest.raises(
        SimulationExecutionUnavailableError
    ):
        await service.cancel_execution(
            execution_id=execution.id,
            user_id=execution.usuario_id,
        )


