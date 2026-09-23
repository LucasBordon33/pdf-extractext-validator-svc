"""Pruebas de integración del endpoint POST /validate (JSON base64)."""

import base64

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.validation import ValidationErrorItem, ValidationResult

client = TestClient(app)


def _payload(name: str, data: bytes) -> dict[str, str]:
    return {"name": name, "content_base64": base64.b64encode(data).decode("ascii")}


def test_validate_returns_ok_for_valid_pdf(valid_pdf: bytes) -> None:
    response = client.post("/validate", json=_payload("documento.pdf", valid_pdf))
    assert response.status_code == 200
    result = ValidationResult.model_validate(response.json())
    assert result.valid is True
    assert result.reason is None
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
    response = client.post("/validate", json=_payload(filename, content))
    assert response.status_code == 200
    result = ValidationResult.model_validate(response.json())
    assert result.valid is False
    assert result.filename == filename
    assert result.errors
    first_error = ValidationErrorItem.model_validate(result.errors[0])
    assert result.reason == first_error.message


def test_validate_sanitizes_filename(valid_pdf: bytes) -> None:
    response = client.post(
        "/validate", json=_payload("..\\fakepath\\doc.pdf", valid_pdf)
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "doc.pdf"


def test_validate_rejects_oversize_payload(oversize_pdf: bytes) -> None:
    response = client.post("/validate", json=_payload("pesado.pdf", oversize_pdf))
    assert response.status_code == 413


def test_validate_rejects_invalid_base64() -> None:
    response = client.post(
        "/validate", json={"name": "x.pdf", "content_base64": "¡no es base64!"}
    )
    assert response.status_code == 422


def test_validate_requires_body_fields() -> None:
    response = client.post("/validate", json={})
    assert response.status_code == 422