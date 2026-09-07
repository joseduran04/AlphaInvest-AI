from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from alphainvest.modules.simulation.domain.enums import (
    SimulationConfigurationStatus,
    SimulationExecutionStatus,
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
    SimulationPortfolioUnavailableError,
)
from alphainvest.modules.simulation.presentation.dependencies import (
    SimulationArchiveContext,
    SimulationCreateContext,
    SimulationExecuteContext,
    SimulationReadContext,
    SimulationServiceDependency,
    SimulationUpdateContext,
)
from alphainvest.modules.simulation.presentation.schemas import (
    SimulationConfigurationArchiveResponse,
    SimulationConfigurationAssetCreateRequest,
    SimulationConfigurationAssetListResponse,
    SimulationConfigurationAssetResponse,
    SimulationConfigurationAssetUpdateRequest,
    SimulationConfigurationCreateRequest,
    SimulationConfigurationListResponse,
    SimulationConfigurationReadyResponse,
    SimulationConfigurationResponse,
    SimulationConfigurationUpdateRequest,
    SimulationDistributionStatusResponse,
    SimulationExecutionCancelResponse,
    SimulationExecutionCreateRequest,
    SimulationExecutionListResponse,
    SimulationExecutionResponse,
    SimulationResultResponse,
)

router = APIRouter(
    prefix="/simulations",
    tags=["Simulaciones"],
)


@router.post(
    "/configurations",
    response_model=SimulationConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear configuración de simulación",
)
async def create_simulation_configuration(
    request: SimulationConfigurationCreateRequest,
    context: SimulationCreateContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationResponse:
    try:
        return await service.create_configuration(
            user_id=context.user.id,
            request=request,
        )
    except SimulationPortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        SimulationConfigurationNameAlreadyExistsError,
        SimulationPortfolioUnavailableError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/configurations",
    response_model=SimulationConfigurationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar configuraciones de simulación",
)
async def list_simulation_configurations(
    context: SimulationReadContext,
    service: SimulationServiceDependency,
    configuration_status: (
        SimulationConfigurationStatus | None
    ) = Query(
        default=None,
        alias="estado",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> SimulationConfigurationListResponse:
    return await service.list_configurations(
        user_id=context.user.id,
        status=configuration_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/configurations/{configuration_id}",
    response_model=SimulationConfigurationResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar configuración de simulación",
)
async def get_simulation_configuration(
    configuration_id: UUID,
    context: SimulationReadContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationResponse:
    try:
        return await service.get_configuration(
            configuration_id=configuration_id,
            user_id=context.user.id,
        )
    except SimulationConfigurationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/configurations/{configuration_id}",
    response_model=SimulationConfigurationResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar configuración de simulación",
)
async def update_simulation_configuration(
    configuration_id: UUID,
    request: SimulationConfigurationUpdateRequest,
    context: SimulationUpdateContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationResponse:
    try:
        return await service.update_configuration(
            configuration_id=configuration_id,
            user_id=context.user.id,
            request=request,
        )
    except (
        SimulationConfigurationNotFoundError,
        SimulationPortfolioNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        SimulationConfigurationNameAlreadyExistsError,
        SimulationConfigurationUnavailableError,
        SimulationPortfolioUnavailableError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.post(
    "/configurations/{configuration_id}/archive",
    response_model=SimulationConfigurationArchiveResponse,
    status_code=status.HTTP_200_OK,
    summary="Archivar configuración de simulación",
)
async def archive_simulation_configuration(
    configuration_id: UUID,
    context: SimulationArchiveContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationArchiveResponse:
    try:
        return await service.archive_configuration(
            configuration_id=configuration_id,
            user_id=context.user.id,
        )
    except SimulationConfigurationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except SimulationConfigurationUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/configurations/{configuration_id}/assets",
    response_model=SimulationConfigurationAssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar activo a configuración",
)
async def add_simulation_configuration_asset(
    configuration_id: UUID,
    request: SimulationConfigurationAssetCreateRequest,
    context: SimulationUpdateContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationAssetResponse:
    try:
        return await service.add_configuration_asset(
            configuration_id=configuration_id,
            user_id=context.user.id,
            request=request,
        )
    except (
        SimulationConfigurationNotFoundError,
        SimulationAssetNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        SimulationConfigurationUnavailableError,
        SimulationAssetUnavailableError,
        SimulationConfigurationAssetAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/configurations/{configuration_id}/assets",
    response_model=SimulationConfigurationAssetListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar activos de configuración",
)
async def list_simulation_configuration_assets(
    configuration_id: UUID,
    context: SimulationReadContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationAssetListResponse:
    try:
        return await service.list_configuration_assets(
            configuration_id=configuration_id,
            user_id=context.user.id,
        )
    except SimulationConfigurationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    (
        "/configurations/{configuration_id}"
        "/assets/{asset_id}"
    ),
    response_model=SimulationConfigurationAssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar activo de configuración",
)
async def update_simulation_configuration_asset(
    configuration_id: UUID,
    asset_id: UUID,
    request: SimulationConfigurationAssetUpdateRequest,
    context: SimulationUpdateContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationAssetResponse:
    try:
        return await service.update_configuration_asset(
            configuration_id=configuration_id,
            asset_id=asset_id,
            user_id=context.user.id,
            request=request,
        )
    except (
        SimulationConfigurationNotFoundError,
        SimulationConfigurationAssetNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        SimulationConfigurationUnavailableError,
        SimulationConfigurationAssetAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    (
        "/configurations/{configuration_id}"
        "/assets/{asset_id}"
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar activo de configuración",
)
async def delete_simulation_configuration_asset(
    configuration_id: UUID,
    asset_id: UUID,
    context: SimulationUpdateContext,
    service: SimulationServiceDependency,
) -> None:
    try:
        await service.delete_configuration_asset(
            configuration_id=configuration_id,
            asset_id=asset_id,
            user_id=context.user.id,
        )
    except (
        SimulationConfigurationNotFoundError,
        SimulationConfigurationAssetNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except SimulationConfigurationUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/configurations/{configuration_id}/distribution",
    response_model=SimulationDistributionStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar estado de distribución",
)
async def get_simulation_distribution_status(
    configuration_id: UUID,
    context: SimulationReadContext,
    service: SimulationServiceDependency,
) -> SimulationDistributionStatusResponse:
    try:
        return await service.get_distribution_status(
            configuration_id=configuration_id,
            user_id=context.user.id,
        )
    except SimulationConfigurationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/configurations/{configuration_id}/ready",
    response_model=SimulationConfigurationReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Marcar configuración como lista",
)
async def mark_simulation_configuration_ready(
    configuration_id: UUID,
    context: SimulationUpdateContext,
    service: SimulationServiceDependency,
) -> SimulationConfigurationReadyResponse:
    try:
        return await service.mark_configuration_ready(
            configuration_id=configuration_id,
            user_id=context.user.id,
        )
    except SimulationConfigurationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        SimulationConfigurationUnavailableError,
        SimulationDistributionInvalidError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/executions",
    response_model=SimulationExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar ejecución de simulación",
)
async def create_simulation_execution(
    request: SimulationExecutionCreateRequest,
    context: SimulationExecuteContext,
    service: SimulationServiceDependency,
) -> SimulationExecutionResponse:
    try:
        return await service.create_execution(
            user_id=context.user.id,
            request=request,
        )
    except (
        SimulationConfigurationNotFoundError,
        SimulationModelVersionNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        SimulationConfigurationUnavailableError,
        SimulationDistributionInvalidError,
        SimulationExecutionAlreadyActiveError,
        SimulationModelVersionUnavailableError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/executions",
    response_model=SimulationExecutionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar ejecuciones de simulación",
)
async def list_simulation_executions(
    context: SimulationReadContext,
    service: SimulationServiceDependency,
    execution_status: (
        SimulationExecutionStatus | None
    ) = Query(
        default=None,
        alias="estado",
    ),
    configuration_id: UUID | None = Query(
        default=None,
        alias="configuracion_id",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> SimulationExecutionListResponse:
    try:
        return await service.list_executions(
            user_id=context.user.id,
            status=execution_status,
            configuration_id=configuration_id,
            limit=limit,
            offset=offset,
        )
    except SimulationConfigurationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/executions/{execution_id}",
    response_model=SimulationExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar ejecución de simulación",
)
async def get_simulation_execution(
    execution_id: UUID,
    context: SimulationReadContext,
    service: SimulationServiceDependency,
) -> SimulationExecutionResponse:
    try:
        return await service.get_execution(
            execution_id=execution_id,
            user_id=context.user.id,
        )
    except SimulationExecutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/executions/{execution_id}/result",
    response_model=SimulationResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultado de simulación",
)
async def get_simulation_execution_result(
    execution_id: UUID,
    context: SimulationReadContext,
    service: SimulationServiceDependency,
) -> SimulationResultResponse:
    try:
        return await service.get_result(
            execution_id=execution_id,
            user_id=context.user.id,
        )
    except SimulationExecutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except SimulationExecutionUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/executions/{execution_id}/cancel",
    response_model=SimulationExecutionCancelResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancelar ejecución de simulación",
)
async def cancel_simulation_execution(
    execution_id: UUID,
    context: SimulationExecuteContext,
    service: SimulationServiceDependency,
) -> SimulationExecutionCancelResponse:
    try:
        return await service.cancel_execution(
            execution_id=execution_id,
            user_id=context.user.id,
        )
    except SimulationExecutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except SimulationExecutionUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


