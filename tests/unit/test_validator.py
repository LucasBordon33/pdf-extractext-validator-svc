"""Suite unitaria del módulo app/core/validator.py."""

import io

import pytest

from app.core.exceptions import (
    CorruptPdfError,
    IncompletePdfError,
    InvalidMimeTypeError,
    NotPdfError,
    ValidationError,
)
from app.core.validator import (
    validate_eof,
    validate_header,
    validate_mime,
    validate_structure,
)

_PDF_BYTES_FIXTURES = ["valid_pdf", "corrupt_pdf", "oversize_pdf"]


def test_domain_exceptions_share_base_class():
    for exc in (NotPdfError, InvalidMimeTypeError, IncompletePdfError, CorruptPdfError):
        assert issubclass(exc, ValidationError)


@pytest.mark.parametrize("fixture_name", _PDF_BYTES_FIXTURES)
def test_validate_mime_accepts_pdf_derived_bytes(fixture_name, request):
    validate_mime(request.getfixturevalue(fixture_name))


def test_validate_mime_rejects_fake_text(fake_pdf_text):
    with pytest.raises(InvalidMimeTypeError):
        validate_mime(fake_pdf_text)


def test_validate_mime_rejects_empty_stream():
    with pytest.raises(InvalidMimeTypeError):
        validate_mime(b"")


@pytest.mark.parametrize("fixture_name", _PDF_BYTES_FIXTURES)
def test_validate_header_accepts_pdf_derived_bytes(fixture_name, request):
    validate_header(request.getfixturevalue(fixture_name))


def test_validate_header_rejects_fake_text(fake_pdf_text):
    with pytest.raises(NotPdfError):
        validate_header(fake_pdf_text)


def test_validate_header_rejects_empty_stream():
    with pytest.raises(NotPdfError):
        validate_header(b"")


def test_validate_eof_accepts_valid_pdf(valid_pdf):
    validate_eof(valid_pdf)


def test_validate_eof_accepts_oversize_pdf(oversize_pdf):
    validate_eof(oversize_pdf)


def test_validate_eof_rejects_corrupt_pdf(corrupt_pdf):
    with pytest.raises(IncompletePdfError):
        validate_eof(corrupt_pdf)


def test_validate_eof_rejects_fake_text(fake_pdf_text):
    with pytest.raises(IncompletePdfError):
        validate_eof(fake_pdf_text)


def test_validate_eof_rejects_empty_stream():
    with pytest.raises(IncompletePdfError):
        validate_eof(b"")


@pytest.mark.parametrize("fixture_name", ["valid_pdf_stream", "oversize_pdf_stream"])
def test_validate_structure_accepts_pdf_streams(fixture_name, request):
    validate_structure(request.getfixturevalue(fixture_name))


@pytest.mark.parametrize(
    "fixture_name", ["corrupt_pdf_stream", "fake_pdf_text_stream"]
)
def test_validate_structure_rejects_invalid_streams(fixture_name, request):
    with pytest.raises(CorruptPdfError):
        validate_structure(request.getfixturevalue(fixture_name))


def test_validate_structure_rejects_empty_stream():
    with pytest.raises(CorruptPdfError):
        validate_structure(io.BytesIO(b""))


def test_validate_structure_is_reusable(valid_pdf_stream):
    validate_structure(valid_pdf_stream)
    validate_structure(valid_pdf_stream)