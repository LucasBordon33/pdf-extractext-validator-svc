"""Pruebas de integración del endpoint POST /api/v1/validate."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.validation import ValidationErrorItem, ValidationResult

client = TestClient(app)


def test_validate_returns_ok_for_valid_pdf(valid_pdf: bytes) -> None:
    response = client.post(
        "/api/v1/validate",
        files={"file": ("documento.pdf", valid_pdf, "application/pdf")},
    )
    assert response.status_code == 200
    result = ValidationResult.model_validate(response.json())
    assert result.is_valid is True
    assert result.filename == "documento.pdf"
    assert result.errors == []


@pytest.mark.parametrize(
    ("fixture_name", "filename"),
    [
        ("corrupt_pdf", "corrupto.pdf"),
        ("fake_pdf_text", "renombrado.pdf"),
    ],
)
def test_validate_returns_200_with_errors(
    fixture_name: str, filename: str, request: pytest.FixtureRequest
) -> None:
    content = request.getfixturevalue(fixture_name)
    response = client.post(
        "/api/v1/validate",
        files={"file": (filename, content, "application/pdf")},
    )
    assert response.status_code == 200
    result = ValidationResult.model_validate(response.json())
    assert result.is_valid is False
    assert result.filename == filename
    assert result.errors
    ValidationErrorItem.model_validate(result.errors[0])


def test_validate_sniffs_content_type_ignoring_client_header(fake_pdf_text: bytes) -> None:
    response = client.post(
        "/api/v1/validate",
        files={"file": ("falso.pdf", fake_pdf_text, "application/pdf")},
    )
    assert response.status_code == 200
    result = ValidationResult.model_validate(response.json())
    assert result.is_valid is False


def test_validate_rejects_oversize_payload(oversize_pdf: bytes) -> None:
    response = client.post(
        "/api/v1/validate",
        files={"file": ("pesado.pdf", oversize_pdf, "application/pdf")},
    )
    assert response.status_code == 413


def test_validate_requires_file_attachment() -> None:
    response = client.post("/api/v1/validate")
    assert response.status_code == 422