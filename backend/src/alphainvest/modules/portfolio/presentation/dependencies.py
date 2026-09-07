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
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.portfolio.application.service import (
    PortfolioService,
)
from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)


def get_portfolio_service(
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> PortfolioService:
    portfolio_repository = PortfolioRepository(
        session
    )
    market_repository = MarketRepository(session)

    return PortfolioService(
        repository=portfolio_repository,
        market_repository=market_repository,
    )


PortfolioServiceDependency = Annotated[
    PortfolioService,
    Depends(get_portfolio_service),
]

PortfolioReadContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "portafolios.leer"
        )
    ),
]

PortfolioCreateContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "portafolios.crear"
        )
    ),
]

PortfolioUpdateContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "portafolios.actualizar"
        )
    ),
]

PortfolioCloseContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "portafolios.cerrar"
        )
    ),
]