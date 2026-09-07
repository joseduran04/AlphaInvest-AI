from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.infrastructure.database.session import (
    get_db_session,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    require_permission,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)
from alphainvest.modules.simulation.application.service import (
    SimulationService,
)
from alphainvest.modules.simulation.infrastructure.repository import (
    SimulationRepository,
)


def get_simulation_service(
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> SimulationService:
    simulation_repository = SimulationRepository(
        session
    )
    portfolio_repository = PortfolioRepository(
        session
    )
    market_repository = MarketRepository(
        session
    )
    ai_repository = AIRepository(session)

    return SimulationService(
        repository=simulation_repository,
        portfolio_repository=portfolio_repository,
        market_repository=market_repository,
        ai_repository=ai_repository,
    )


SimulationServiceDependency = Annotated[
    SimulationService,
    Depends(get_simulation_service),
]

SimulationReadContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "simulaciones.leer"
        )
    ),
]

SimulationCreateContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "simulaciones.crear"
        )
    ),
]

SimulationUpdateContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "simulaciones.actualizar"
        )
    ),
]

SimulationArchiveContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "simulaciones.archivar"
        )
    ),
]

SimulationExecuteContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "simulaciones.ejecutar"
        )
    ),
]