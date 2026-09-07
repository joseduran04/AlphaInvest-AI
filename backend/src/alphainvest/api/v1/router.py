from fastapi import APIRouter

from alphainvest.api.v1.health import (
    router as health_router,
)
from alphainvest.modules.ai.presentation.router import (
    router as ai_router,
)
from alphainvest.modules.auth.presentation.router import (
    router as auth_router,
)
from alphainvest.modules.market.presentation.router import (
    router as market_router,
)
from alphainvest.modules.news.presentation.router import (
    router as news_router,
)
from alphainvest.modules.operation.presentation.router import (
    router as operation_router,
)
from alphainvest.modules.portfolio.presentation.router import (
    router as portfolio_router,
)
from alphainvest.modules.profile.presentation.router import (
    router as profile_router,
)
from alphainvest.modules.reporting.presentation.router import (
    router as reporting_router,
)
from alphainvest.modules.simulation.presentation.router import (
    router as simulation_router,
)

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(market_router)
api_router.include_router(portfolio_router)
api_router.include_router(simulation_router)
api_router.include_router(ai_router)
api_router.include_router(news_router)
api_router.include_router(operation_router)
api_router.include_router(reporting_router)