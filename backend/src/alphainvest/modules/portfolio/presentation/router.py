from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Response,
    status,
)

from alphainvest.modules.portfolio.domain.enums import (
    PortfolioStatus,
)
from alphainvest.modules.portfolio.domain.exceptions import (
    PortfolioAssetNotFoundError,
    PortfolioAssetUnavailableError,
    PortfolioNameAlreadyExistsError,
    PortfolioNotFoundError,
    PortfolioUnavailableError,
    PositionAlreadyExistsError,
    PositionNotFoundError,
)
from alphainvest.modules.portfolio.presentation.dependencies import (
    PortfolioCloseContext,
    PortfolioCreateContext,
    PortfolioReadContext,
    PortfolioServiceDependency,
    PortfolioUpdateContext,
)
from alphainvest.modules.portfolio.presentation.schemas import (
    AssetAllocationResponse,
    PortfolioCloseResponse,
    PortfolioCreateRequest,
    PortfolioListResponse,
    PortfolioOverviewResponse,
    PortfolioResponse,
    PortfolioUpdateRequest,
    PortfolioValuationCreateRequest,
    PortfolioValuationListResponse,
    PortfolioValuationResponse,
    PositionCreateRequest,
    PositionListResponse,
    PositionResponse,
    PositionUpdateRequest,
    SectorAllocationResponse,
)

router = APIRouter(
    prefix="/portfolios",
    tags=["Portafolios"],
)


@router.post(
    "",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear portafolio",
)
async def create_portfolio(
    request: PortfolioCreateRequest,
    context: PortfolioCreateContext,
    service: PortfolioServiceDependency,
) -> PortfolioResponse:
    try:
        return await service.create_portfolio(
            user_id=context.user.id,
            request=request,
        )
    except PortfolioNameAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=PortfolioListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar portafolios propios",
)
async def list_portfolios(
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
    estado: PortfolioStatus | None = Query(
        default=None,
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
) -> PortfolioListResponse:
    return await service.list_portfolios(
        user_id=context.user.id,
        status=estado,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar portafolio",
)
async def get_portfolio(
    portfolio_id: UUID,
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
) -> PortfolioResponse:
    try:
        return await service.get_portfolio(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{portfolio_id}/summary",
    response_model=PortfolioOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar resumen del portafolio",
)
async def get_portfolio_summary(
    portfolio_id: UUID,
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
) -> PortfolioOverviewResponse:
    try:
        return await service.get_portfolio_summary(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{portfolio_id}/allocation/assets",
    response_model=AssetAllocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar distribución por activo",
)
async def get_asset_allocation(
    portfolio_id: UUID,
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
) -> AssetAllocationResponse:
    try:
        return await service.get_asset_allocation(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{portfolio_id}/allocation/sectors",
    response_model=SectorAllocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar distribución por sector",
)
async def get_sector_allocation(
    portfolio_id: UUID,
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
) -> SectorAllocationResponse:
    try:
        return await service.get_sector_allocation(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar portafolio",
)
async def update_portfolio(
    portfolio_id: UUID,
    request: PortfolioUpdateRequest,
    context: PortfolioUpdateContext,
    service: PortfolioServiceDependency,
) -> PortfolioResponse:
    try:
        return await service.update_portfolio(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
            request=request,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PortfolioNameAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except PortfolioUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/{portfolio_id}/valuations",
    response_model=PortfolioValuationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar valoración histórica",
)
async def register_portfolio_valuation(
    portfolio_id: UUID,
    request: PortfolioValuationCreateRequest,
    context: PortfolioUpdateContext,
    service: PortfolioServiceDependency,
) -> PortfolioValuationResponse:
    try:
        return await service.register_portfolio_valuation(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
            request=request,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{portfolio_id}/valuations",
    response_model=PortfolioValuationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar historial de valoraciones",
)
async def list_portfolio_valuations(
    portfolio_id: UUID,
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> PortfolioValuationListResponse:
    try:
        return await service.list_portfolio_valuations(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
            limit=limit,
            offset=offset,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/{portfolio_id}/close",
    response_model=PortfolioCloseResponse,
    status_code=status.HTTP_200_OK,
    summary="Cerrar portafolio",
)
async def close_portfolio(
    portfolio_id: UUID,
    context: PortfolioCloseContext,
    service: PortfolioServiceDependency,
) -> PortfolioCloseResponse:
    try:
        return await service.close_portfolio(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PortfolioUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/{portfolio_id}/positions",
    response_model=PositionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar posición virtual",
)
async def create_position(
    portfolio_id: UUID,
    request: PositionCreateRequest,
    context: PortfolioUpdateContext,
    service: PortfolioServiceDependency,
) -> PositionResponse:
    try:
        return await service.create_position(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
            request=request,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PortfolioAssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (
        PortfolioUnavailableError,
        PortfolioAssetUnavailableError,
        PositionAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/{portfolio_id}/positions",
    response_model=PositionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar posiciones virtuales",
)
async def list_positions(
    portfolio_id: UUID,
    context: PortfolioReadContext,
    service: PortfolioServiceDependency,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> PositionListResponse:
    try:
        return await service.list_positions(
            portfolio_id=portfolio_id,
            user_id=context.user.id,
            limit=limit,
            offset=offset,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{portfolio_id}/positions/{position_id}",
    response_model=PositionResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar posición virtual",
)
async def update_position(
    portfolio_id: UUID,
    position_id: UUID,
    request: PositionUpdateRequest,
    context: PortfolioUpdateContext,
    service: PortfolioServiceDependency,
) -> PositionResponse:
    try:
        return await service.update_position(
            portfolio_id=portfolio_id,
            position_id=position_id,
            user_id=context.user.id,
            request=request,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PositionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PortfolioUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    "/{portfolio_id}/positions/{position_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar posición virtual",
)
async def delete_position(
    portfolio_id: UUID,
    position_id: UUID,
    context: PortfolioUpdateContext,
    service: PortfolioServiceDependency,
) -> Response:
    try:
        await service.delete_position(
            portfolio_id=portfolio_id,
            position_id=position_id,
            user_id=context.user.id,
        )
    except PortfolioNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PositionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PortfolioUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )