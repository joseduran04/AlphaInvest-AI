from fastapi import APIRouter

from alphainvest.api.v1.health import router as health_router
from alphainvest.modules.auth.presentation.router import router as auth_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
