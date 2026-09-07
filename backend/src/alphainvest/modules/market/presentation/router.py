from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from alphainvest.modules.market.domain.enums import (
    AssetStatus,
)
from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    HistoricalPriceNotFoundError,
    IndicatorCalculationError,
    InsufficientPriceHistoryError,
    InvalidPriceDateRangeError,
    JobExecutionNotFoundError,
    PriceSynchronizationError,
    ProcessLockUnavailableError,
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
    ScheduledJobNotFoundError,
)
from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.modules.market.presentation.dependencies import (
    FinancialIndicatorServiceDependency,
    IndicatorCalculateContext,
    IndicatorReadContext,
    JobReadContext,
    MarketExecutionServiceDependency,
    MarketReadContext,
    MarketServiceDependency,
    PriceReadContext,
    PriceSynchronizationServiceDependency,
    PriceWriteContext,
    SourceReadContext,
)
from alphainvest.modules.market.presentation.schemas import (
    AssetListResponse,
    AssetResponse,
    AssetTypeListResponse,
    FinancialIndicatorListResponse,
    FinancialSourceListResponse,
    HistoricalPriceListResponse,
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    LatestPriceResponse,
    MarketListResponse,
    PriceSynchronizationResponse,
)
from alphainvest.modules.operation.domain.enums import (
    JobExecutionStatus,
)
from alphainvest.modules.operation.presentation.schemas import (
    JobExecutionListResponse,
    JobExecutionResponse,
)

router = APIRouter(
    prefix="/market",
    tags=["Mercado"],
)


@router.get(
    "/markets",
    response_model=MarketListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar mercados",
)
async def list_markets(
    _: MarketReadContext,
    service: MarketServiceDependency,
    active_only: bool = Query(default=True),
) -> MarketListResponse:
    return await service.list_markets(
        active_only=active_only
    )


@router.get(
    "/asset-types",
    response_model=AssetTypeListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar tipos de activo",
)
async def list_asset_types(
    _: MarketReadContext,
    service: MarketServiceDependency,
    active_only: bool = Query(default=True),
) -> AssetTypeListResponse:
    return await service.list_asset_types(
        active_only=active_only
    )


@router.get(
    "/sources",
    response_model=FinancialSourceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar fuentes financieras",
)
async def list_financial_sources(
    _: SourceReadContext,
    service: MarketServiceDependency,
    active_only: bool = Query(default=True),
) -> FinancialSourceListResponse:
    return await service.list_financial_sources(
        active_only=active_only
    )


@router.get(
    "/assets",
    response_model=AssetListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar activos financieros",
)
async def list_assets(
    _: MarketReadContext,
    service: MarketServiceDependency,
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=200,
    ),
    market_code: str | None = Query(
        default=None,
        min_length=1,
        max_length=30,
    ),
    asset_type_code: str | None = Query(
        default=None,
        min_length=1,
        max_length=30,
    ),
    sector: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    currency: str | None = Query(
        default=None,
        min_length=3,
        max_length=3,
        pattern="^[A-Za-z]{3}$",
    ),
    asset_status: AssetStatus | None = Query(
        default=AssetStatus.ACTIVE,
        alias="status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AssetListResponse:
    return await service.list_assets(
        search=search,
        market_code=market_code,
        asset_type_code=asset_type_code,
        sector=sector,
        currency=currency,
        status=asset_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/assets/{asset_id}",
    response_model=AssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de activo",
)
async def get_asset(
    asset_id: UUID,
    _: MarketReadContext,
    service: MarketServiceDependency,
) -> AssetResponse:
    try:
        return await service.get_asset(
            asset_id=asset_id
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/assets/{asset_id}/prices",
    response_model=HistoricalPriceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar precios históricos",
)
async def get_asset_price_history(
    asset_id: UUID,
    _: PriceReadContext,
    service: MarketServiceDependency,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    source_id: UUID | None = Query(default=None),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> HistoricalPriceListResponse:
    try:
        return await service.get_asset_price_history(
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
            source_id=source_id,
            limit=limit,
            offset=offset,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except FinancialSourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidPriceDateRangeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.get(
    "/assets/{asset_id}/latest-price",
    response_model=LatestPriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar último precio disponible",
)
async def get_latest_asset_price(
    asset_id: UUID,
    _: PriceReadContext,
    service: MarketServiceDependency,
    source_id: UUID | None = Query(default=None),
) -> LatestPriceResponse:
    try:
        return await service.get_latest_asset_price(
            asset_id=asset_id,
            source_id=source_id,
        )
    except (
        AssetNotFoundError,
        FinancialSourceNotFoundError,
        HistoricalPriceNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/assets/{asset_id}/prices/sync",
    response_model=PriceSynchronizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Sincronizar precios diarios",
    description=(
        "Consulta Alpha Vantage y realiza upsert de los "
        "precios diarios del activo."
    ),
)
async def synchronize_asset_prices(
    asset_id: UUID,
    context: PriceWriteContext,
    service: PriceSynchronizationServiceDependency,
) -> PriceSynchronizationResponse:
    try:
        return await service.synchronize_asset(
            asset_id=asset_id,
            requested_by=context.user.id,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except FinancialSourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ScheduledJobNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except ProcessLockUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ProviderConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except ProviderRateLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(error),
        ) from error
    except (
        ProviderRequestError,
        ProviderResponseError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error
    except PriceSynchronizationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.post(
    "/assets/{asset_id}/indicators/calculate",
    response_model=IndicatorCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcular indicadores financieros",
    description=(
        "Calcula y persiste indicadores técnicos usando "
        "los precios históricos de una fuente específica."
    ),
)
async def calculate_asset_indicators(
    asset_id: UUID,
    request: IndicatorCalculationRequest,
    _: IndicatorCalculateContext,
    service: FinancialIndicatorServiceDependency,
) -> IndicatorCalculationResponse:
    try:
        return await service.calculate_indicators(
            asset_id=asset_id,
            request=request,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except FinancialSourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InsufficientPriceHistoryError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except IndicatorCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.get(
    "/assets/{asset_id}/indicators",
    response_model=FinancialIndicatorListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar indicadores financieros",
)
async def list_asset_indicators(
    asset_id: UUID,
    _: IndicatorReadContext,
    service: FinancialIndicatorServiceDependency,
    indicator_type: FinancialIndicatorType | None = Query(
        default=None,
    ),
    period: str | None = Query(
        default=None,
        min_length=2,
        max_length=30,
        pattern=(
            r"^(?:[1-9][0-9]*D|"
            r"[1-9][0-9]*-[1-9][0-9]*-"
            r"[1-9][0-9]*)$"
        ),
    ),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> FinancialIndicatorListResponse:
    try:
        return await service.list_indicators(
            asset_id=asset_id,
            indicator_type=indicator_type,
            period=period,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidPriceDateRangeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.get(
    "/synchronizations",
    response_model=JobExecutionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar sincronizaciones de mercado",
)
async def list_market_synchronizations(
    _: JobReadContext,
    service: MarketExecutionServiceDependency,
    execution_status: JobExecutionStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> JobExecutionListResponse:
    return await service.list_synchronizations(
        status=execution_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/synchronizations/{execution_id}",
    response_model=JobExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar sincronización de mercado",
)
async def get_market_synchronization(
    execution_id: UUID,
    _: JobReadContext,
    service: MarketExecutionServiceDependency,
) -> JobExecutionResponse:
    try:
        return await service.get_synchronization(
            execution_id
        )
    except JobExecutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error