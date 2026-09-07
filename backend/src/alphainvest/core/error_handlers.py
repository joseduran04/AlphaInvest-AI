import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from alphainvest.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _error_payload(
    *, code: str, message: str, details: Any = None, request_id: str | None = None
) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "meta": {"request_id": request_id},
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request_id=request_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)

        return JSONResponse(
            status_code=422,
            content=_error_payload(
                code="validation_error",
                message="Los datos enviados no son válidos",
                details=jsonable_encoder(exc.errors()),
                request_id=request_id,
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception("unexpected_error", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                code="internal_server_error",
                message="Ocurrió un error interno",
                request_id=request_id,
            ),
        )
