"""Integración Consul del microservicio validador.

La implementación (cliente, registro, health, lifespan) vive en el
paquete compartido `app.infrastructure.service_discovery`; aquí solo se
liga la identidad del servicio con el entorno (composition root).
"""

from fastapi import FastAPI

from app.infrastructure.service_discovery import (
    ConsulAgentClient,
    ConsulServiceRegistry,
    attach_consul_lifespan,
    load_settings,
)

_SERVICE_DEFAULTS = {
    "service_name": "validator",
    "service_port": 8001,
    "service_health_path": "/health",
}


def build_registry() -> ConsulServiceRegistry:
    """Registro de Consul configurado con la identidad del validador."""
    settings = load_settings(**_SERVICE_DEFAULTS)
    return ConsulServiceRegistry(ConsulAgentClient(settings), settings)


def attach_consul(app: FastAPI) -> None:
    """Registro al iniciar y desregistro al apagar (SIGINT/SIGTERM)."""
    attach_consul_lifespan(app, build_registry())
