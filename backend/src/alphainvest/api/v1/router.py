from fastapi import APIRouter

from alphainvest.api.v1.health import router as health_router
from alphainvest.modules.auth.presentation.router import router as auth_router
from alphainvest.modules.market.presentation.router import (
    router as market_router,
)
from alphainvest.modules.profile.presentation.router import (
    router as profile_router,
)

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(market_router)
