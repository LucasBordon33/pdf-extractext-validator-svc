"""DTOs del contrato de la API de validación."""

from pydantic import BaseModel, Field


class ValidationErrorItem(BaseModel):
    """Representa un error de validación individual."""

    code: str = Field(
        ...,
        description="Código máquina del error (mapeo de ValidationError.code).",
        examples=["INVALID_MIME_TYPE"],
    )
    message: str = Field(
        ...,
        description="Mensaje legible del error.",
        examples=["el tipo detectado es 'text/plain', se esperaba application/pdf"],
    )
    detail: str | None = Field(
        default=None,
        description="Detalle adicional opcional.",
        examples=["pypdf: PdfStreamError"],
    )


class ValidationResult(BaseModel):
    """Contrato de respuesta principal del endpoint /validate."""

    valid: bool = Field(
        ...,
        description="Indica si el documento es un PDF íntegro.",
        examples=[True],
    )
    reason: str | None = Field(
        default=None,
        description="Mensaje del primer error; presente solo cuando valid es false.",
        examples=["el tipo detectado es 'text/plain', se esperaba application/pdf"],
    )
    filename: str = Field(
        ...,
        description="Nombre del archivo enviado (sanitizado).",
        examples=["documento.pdf"],
    )
    errors: list[ValidationErrorItem] = Field(
        default_factory=list,
        description="Errores encontrados; vacío cuando valid es true.",
        examples=[[]],
    )