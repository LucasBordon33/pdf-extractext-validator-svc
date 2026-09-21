"""Configuración de la aplicación, cargada desde variables de entorno."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de ejecución del servicio de validación de PDF."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "pdf-validator-service"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 10
    PORT: int = 8001


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia única de Settings para todo el proceso."""
    return Settings()