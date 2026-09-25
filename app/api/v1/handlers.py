"""Manejadores globales de error: respuestas JSON estables sin fuga de trazas."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_request_id

logger = logging.getLogger("pdf-validator-service")

_INTERNAL_ERROR_MESSAGE = "Internal Server Error"


def _trace_id(request: Request) -> str:
    """request_id de la petición actual, desde el scope o el contexto de logging."""
    return request.scope.get("request_id") or get_request_id()


def register_exception_handlers(app: FastAPI) -> None:
    """Registra en la instancia de FastAPI el fallback global para errores no capturados."""

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _trace_id(request)
        logger.error(
            "unhandled exception",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": 500,
            },
        )
        return JSONResponse(
            status_code=500,
            content={"detail": _INTERNAL_ERROR_MESSAGE, "request_id": request_id},
        )