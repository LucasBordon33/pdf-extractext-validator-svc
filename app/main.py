"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.validator import router as validator_router
from app.api.v1.handlers import register_exception_handlers
from app.config import get_settings
from app.core.logging import RequestContextMiddleware, configure_logging

settings = get_settings()

configure_logging()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.add_middleware(RequestContextMiddleware)
register_exception_handlers(app)
app.include_router(health_router)
app.include_router(validator_router)