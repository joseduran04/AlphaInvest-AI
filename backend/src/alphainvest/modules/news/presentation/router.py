from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    ProcessLockUnavailableError,
    ScheduledJobNotFoundError,
)
from alphainvest.modules.news.domain.exceptions import (
    InvalidNewsDateRangeError,
    NewsDocumentNotFoundError,
    NewsProviderConfigurationError,
    NewsProviderRateLimitError,
    NewsProviderRequestError,
    NewsProviderResponseError,
    NewsSynchronizationError,
)
from alphainvest.modules.news.presentation.dependencies import (
    NewsReadContext,
    NewsServiceDependency,
    NewsSynchronizationServiceDependency,
    NewsWriteContext,
)
from alphainvest.modules.news.presentation.schemas import (
    NewsListResponse,
    NewsSynchronizationResponse,
)

router = APIRouter(
    prefix="/news",
    tags=["Noticias"],
)


@router.get(
    "/assets/{asset_id}",
    response_model=NewsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar noticias de un activo",
    description=(
        "Consulta noticias financieras persistidas "
        "para un activo y recupera su contenido "
        "documental desde MongoDB."
    ),
)
async def list_asset_news(
    asset_id: UUID,
    _: NewsReadContext,
    service: NewsServiceDependency,
    start_at: datetime | None = Query(
        default=None
    ),
    end_at: datetime | None = Query(
        default=None
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
) -> NewsListResponse:
    try:
        return await service.list_asset_news(
            asset_id=asset_id,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
            offset=offset,
        )

    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except InvalidNewsDateRangeError as error:
        raise HTTPException(
            status_code=(
                status
                .HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error

    except NewsDocumentNotFoundError as error:
        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(error),
        ) from error


@router.post(
    "/assets/{asset_id}/sync",
    response_model=(
        NewsSynchronizationResponse
    ),
    status_code=status.HTTP_200_OK,
    summary=(
        "Sincronizar noticias de un activo"
    ),
    description=(
        "Consulta Alpha Vantage NEWS_SENTIMENT "
        "y persiste las noticias relacionadas "
        "con el activo."
    ),
)
async def synchronize_asset_news(
    asset_id: UUID,
    context: NewsWriteContext,
    service: (
        NewsSynchronizationServiceDependency
    ),
    start_at: datetime | None = Query(
        default=None
    ),
    end_at: datetime | None = Query(
        default=None
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> NewsSynchronizationResponse:
    try:
        return await service.synchronize_asset(
            asset_id=asset_id,
            requested_by=context.user.id,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except FinancialSourceNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except ScheduledJobNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(error),
        ) from error

    except ProcessLockUnavailableError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error

    except NewsProviderConfigurationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(error),
        ) from error

    except NewsProviderRateLimitError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=str(error),
        ) from error

    except (
        NewsProviderRequestError,
        NewsProviderResponseError,
    ) as error:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status
                .HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error

    except NewsSynchronizationError as error:
        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(error),
        ) from error