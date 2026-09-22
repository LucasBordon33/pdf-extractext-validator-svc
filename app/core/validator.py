"""Chequeos superficiales de bajo costo sobre bytes puros.

Capa de dominio: sin dependencias de FastAPI ni HTTP. Cada función lanza
su excepción de dominio ante una falla de validación.
"""

import magic

from app.core.exceptions import (
    IncompletePdfError,
    InvalidMimeTypeError,
    NotPdfError,
)

_EOF_WINDOW_BYTES = 1024


def validate_mime(data: bytes) -> None:
    """Sniffing MIME sobre los bytes; debe detectar application/pdf."""
    if not data:
        raise InvalidMimeTypeError("un stream vacío nunca es application/pdf")
    detected = magic.from_buffer(data, mime=True)
    if detected != "application/pdf":
        raise InvalidMimeTypeError(
            f"el tipo detectado es {detected!r}, se esperaba application/pdf"
        )


def validate_header(data: bytes) -> None:
    """Verifica que el stream comience con la firma b'%PDF'."""
    if not data.startswith(b"%PDF"):
        raise NotPdfError("el stream no comienza con la firma '%PDF'")


def validate_eof(data: bytes) -> None:
    """Verifica el marcador b'%%EOF' en la ventana final del stream."""
    if b"%%EOF" not in data[-_EOF_WINDOW_BYTES:]:
        raise IncompletePdfError("falta el marcador '%%EOF' al final del documento")