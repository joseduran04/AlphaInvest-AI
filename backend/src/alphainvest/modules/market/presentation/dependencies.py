from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)


def get_market_service(
    session: AsyncSession = Depends(get_db_session),
) -> MarketService:
    repository = MarketRepository(session)

    return MarketService(repository)


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