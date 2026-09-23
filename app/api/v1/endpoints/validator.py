"""Endpoint de validación de documentos (POST /validate)."""

import base64
import io
import os

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.core.exceptions import ValidationError
from app.core.validator import (
    validate_eof,
    validate_header,
    validate_mime,
    validate_structure,
)
from app.schemas.validation import (
    ValidationErrorItem,
    ValidationRequest,
    ValidationResult,
)

router = APIRouter()

_SHALLOW_CHECKS = (validate_mime, validate_header, validate_eof)


def _to_error_item(exc: ValidationError) -> ValidationErrorItem:
    return ValidationErrorItem(code=exc.code, message=exc.message, detail=exc.detail)


def _sanitized_filename(name: str) -> str:
    return os.path.basename(name.replace("\\", "/"))


@router.post("/validate", response_model=ValidationResult)
async def validate(payload: ValidationRequest) -> ValidationResult:
    """Valida el contenido base64 de un PDF en memoria y devuelve el resultado."""
    max_bytes = get_settings().MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(payload.content_base64) // 4 * 3 > max_bytes:
        raise HTTPException(
            status_code=413, detail="el archivo supera el límite de tamaño permitido"
        )

    try:
        data = base64.b64decode(payload.content_base64, validate=True)
    except ValueError:
        raise HTTPException(
            status_code=422, detail="content_base64 no es base64 válido"
        ) from None

    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413, detail="el archivo supera el límite de tamaño permitido"
        )
    if not data:
        raise HTTPException(status_code=422, detail="el archivo está vacío")

    errors: list[ValidationErrorItem] = []
    for check in _SHALLOW_CHECKS:
        try:
            check(data)
        except ValidationError as exc:
            errors.append(_to_error_item(exc))
            break
    else:
        try:
            validate_structure(io.BytesIO(data))
        except ValidationError as exc:
            errors.append(_to_error_item(exc))

    return ValidationResult(
        valid=not errors,
        reason=errors[0].message if errors else None,
        filename=_sanitized_filename(payload.name),
        errors=errors,
    )