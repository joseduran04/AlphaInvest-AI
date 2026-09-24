import logging
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        started_at = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response


logger = logging.getLogger(__name__)


class UnhandledErrorMiddleware(BaseHTTPMiddleware):
    """Convierte errores no controlados en una respuesta JSON 500.

    Debe registrarse como el middleware más interno: así la respuesta
    de error atraviesa CORSMiddleware y el navegador puede leerla. Sin
    esto, Starlette responde el 500 fuera de CORS y el frontend solo ve
    "No fue posible conectar con el servidor".
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except Exception:
            request_id = getattr(request.state, "request_id", None)
            logger.exception(
                "unexpected_error",
                extra={"request_id": request_id},
            )

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "internal_server_error",
                        "message": "Ocurrió un error interno",
                        "details": None,
                    },
                    "meta": {"request_id": request_id},
                },
            )
