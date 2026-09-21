"""Excepciones de dominio para la validación de PDFs."""


class ValidationError(Exception):
    """Base de todas las excepciones de validación."""


class NotPdfError(ValidationError):
    """El stream no comienza con el marcador '%PDF'."""


class InvalidMimeTypeError(ValidationError):
    """El tipo MIME real (sniffing) no es application/pdf."""


class IncompletePdfError(ValidationError):
    """El stream está incompleto o el marcador '%%EOF' no aparece en la cola."""


class CorruptPdfError(ValidationError):
    """La estructura interna no pudo leerse con pypdf."""