from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from alphainvest.core.config import get_settings
from alphainvest.infrastructure.database.health import check_database
from alphainvest.infrastructure.database.session import engine
from alphainvest.infrastructure.mongodb.client import (
    get_mongo_client,
)
from alphainvest.infrastructure.mongodb.health import (
    check_mongodb,
)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def liveness(request: Request) -> dict[str, object]:
    settings = get_settings()
    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": settings.name,
            "version": settings.version,
            "environment": settings.env,
        },
        "meta": {"request_id": request.state.request_id},
    }


@router.get("/ready")
async def readiness(request: Request) -> JSONResponse:
    db = await check_database(engine)

    mongo = await check_mongodb(
        get_mongo_client()
    )

    ready = (
        db.status == "up"
        and mongo.status == "up"
    )

    return JSONResponse(
        status_code=(
            status.HTTP_200_OK
            if ready
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "success": ready,
            "data": {
                "status": (
                    "ready"
                    if ready
                    else "not_ready"
                ),
                "api": "up",
                "database": db.status,
                "database_latency_ms": (
                    db.latency_ms
                ),
                "database_error_type": (
                    db.error
                ),
                "mongodb": mongo.status,
                "mongodb_latency_ms": (
                    mongo.latency_ms
                ),
                "mongodb_error_type": (
                    mongo.error
                ),
            },
            "meta": {
                "request_id": (
                    request.state.request_id
                )
            },
        },
    )


@router.get("")
async def health_alias(request: Request) -> JSONResponse:
    """Compatibilidad con el endpoint validado en el Entregable 01."""
    return await readiness(request)
