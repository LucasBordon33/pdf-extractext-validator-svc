"""Excepciones de dominio para la validación de documentos.

Desacopladas de FastAPI y de cualquier biblioteca HTTP: son la fuente de
verdad que la capa HTTP mapea a ValidationResult/ValidationErrorItem.
"""


class ValidationError(Exception):
    """Base de todas las fallas de validación."""

    code: str = "VALIDATION_ERROR"

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class NotPdfError(ValidationError):
    """Los bytes no corresponden a la firma o estructura base de un PDF."""

    code = "NOT_PDF"


class InvalidMimeTypeError(ValidationError):
    """El tipo MIME detectado difiere de application/pdf."""

    code = "INVALID_MIME_TYPE"


class IncompletePdfError(ValidationError):
    """El archivo está truncado o carece del marcador de cierre %%EOF."""

    code = "INCOMPLETE_PDF"


class CorruptPdfError(ValidationError):
    """La estructura interna del PDF es ilegible (corrupta)."""

    code = "CORRUPT_PDF"