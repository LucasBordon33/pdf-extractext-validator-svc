"""Endpoint de monitoreo para liveness de contenedores (Docker/CI)."""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Devuelve el estado del servicio y su versión."""
    settings = get_settings()
    return {"status": "ok", "version": settings.APP_VERSION}