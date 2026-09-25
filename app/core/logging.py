"""Logging estructurado en JSON a stdout para entornos sin estado."""

import contextvars
import json
import logging
import sys
import time
import traceback
import uuid
from datetime import UTC, datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

_request_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


def get_request_id() -> str:
    """Devuelve el request_id de la petición en curso."""
    return _request_id.get()


class JsonLogFormatter(logging.Formatter):
    """Serializa cada registro a una línea JSON con campos seguros y conocidos."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": get_settings().APP_NAME,
            "request_id": _request_id.get() or record.__dict__.get("request_id", ""),
            "filename": record.__dict__.get("file_name"),
            "duration_ms": record.__dict__.get("duration_ms"),
            "method": record.__dict__.get("method"),
            "path": record.__dict__.get("path"),
            "status": record.__dict__.get("status"),
        }
        if record.exc_info:
            entry["exception"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(entry, ensure_ascii=False)


def configure_logging() -> None:
    """Aplica el formato JSON al root y a los loggers de uvicorn."""
    level = logging.getLevelName(get_settings().LOG_LEVEL.upper())
    if not isinstance(level, int):
        level = logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers[:] = [handler]
        uvicorn_logger.propagate = False


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Inyecta request_id, mide duración y emite el log de acceso en JSON."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        token = _request_id.set(request_id)
        started = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            logging.getLogger("pdf-validator-service").info(
                "request completed",
                extra={
                    "request_id": request_id,
                    "duration_ms": duration_ms,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code if response is not None else 500,
                },
            )
            _request_id.reset(token)
        return response