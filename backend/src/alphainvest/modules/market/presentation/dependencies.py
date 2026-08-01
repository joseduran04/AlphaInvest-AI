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


def get_market_service(
    session: AsyncSession = Depends(get_db_session),
) -> MarketService:
    repository = MarketRepository(session)

    return MarketService(repository)

def get_price_synchronization_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> PriceSynchronizationService:
    repository = MarketRepository(session)
    provider = create_alpha_vantage_provider(settings)

    return PriceSynchronizationService(
        repository=repository,
        provider=provider,
    )

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