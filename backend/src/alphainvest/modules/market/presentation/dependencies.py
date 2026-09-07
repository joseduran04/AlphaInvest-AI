from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.core.config import Settings, get_settings
from alphainvest.infrastructure.database.session import (
    get_db_session,
)
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    require_permission,
)
from alphainvest.modules.market.application.execution_service import (
    MarketExecutionService,
)
from alphainvest.modules.market.application.indicator_service import (
    FinancialIndicatorService,
)
from alphainvest.modules.market.application.service import (
    MarketService,
)
from alphainvest.modules.market.application.synchronization_service import (
    PriceSynchronizationService,
)
from alphainvest.modules.market.infrastructure.providers.factory import (
    create_alpha_vantage_provider,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)


def get_market_service(
    session: AsyncSession = Depends(get_db_session),
) -> MarketService:
    repository = MarketRepository(session)

    return MarketService(repository)


def get_financial_indicator_service(
    session: AsyncSession = Depends(get_db_session),
) -> FinancialIndicatorService:
    repository = MarketRepository(session)

    return FinancialIndicatorService(repository)


def get_price_synchronization_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> PriceSynchronizationService:
    market_repository = MarketRepository(session)
    operation_repository = OperationRepository(session)
    provider = create_alpha_vantage_provider(settings)

    return PriceSynchronizationService(
        market_repository=market_repository,
        operation_repository=operation_repository,
        provider=provider,
    )

def get_market_execution_service(
    session: AsyncSession = Depends(get_db_session),
) -> MarketExecutionService:
    repository = OperationRepository(session)

    return MarketExecutionService(repository)

MarketServiceDependency = Annotated[
    MarketService,
    Depends(get_market_service),
]

MarketReadContext = Annotated[
    AuthContext,
    Depends(require_permission("activos.leer")),
]

SourceReadContext = Annotated[
    AuthContext,
    Depends(require_permission("fuentes.leer")),
]

PriceReadContext = Annotated[
    AuthContext,
    Depends(require_permission("precios.leer")),
]

PriceSynchronizationServiceDependency = Annotated[
    PriceSynchronizationService,
    Depends(get_price_synchronization_service),
]

PriceWriteContext = Annotated[
    AuthContext,
    Depends(require_permission("precios.cargar")),
]

JobReadContext = Annotated[
    AuthContext,
    Depends(require_permission("trabajos.leer")),
]

MarketExecutionServiceDependency = Annotated[
    MarketExecutionService,
    Depends(get_market_execution_service),
]

FinancialIndicatorServiceDependency = Annotated[
    FinancialIndicatorService,
    Depends(get_financial_indicator_service),
]

IndicatorReadContext = Annotated[
    AuthContext,
    Depends(require_permission("indicadores.leer")),
]

IndicatorCalculateContext = Annotated[
    AuthContext,
    Depends(require_permission("indicadores.calcular")),
]