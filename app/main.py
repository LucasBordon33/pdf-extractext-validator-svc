"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.validator import router as validator_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.include_router(health_router)
app.include_router(validator_router)