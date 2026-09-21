"""Generadores de archivos de prueba en memoria (sin ficheros en disco)."""

import io
import math

import pytest
from pypdf import PdfWriter

# TODO: alinear con Settings.MAX_UPLOAD_SIZE_MB cuando exista app/config.py
MAX_UPLOAD_MB = 10
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def _write_valid_pdf() -> bytes:
    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture(scope="session")
def valid_pdf() -> bytes:
    return _write_valid_pdf()


@pytest.fixture()
def corrupt_pdf(valid_pdf: bytes) -> bytes:
    return valid_pdf[: len(valid_pdf) // 2]


@pytest.fixture()
def fake_pdf_text() -> bytes:
    return b"this is plain text pretending to be a pdf, rename me.txt\n" * 40


@pytest.fixture(scope="session")
def oversize_pdf(valid_pdf: bytes) -> bytes:
    line = b"%" + b" " * 253 + b"\n"
    padding = line * math.ceil(MAX_UPLOAD_BYTES / len(line))
    return b"%PDF-1.4\n" + padding + valid_pdf[8:]


@pytest.fixture()
def valid_pdf_stream(valid_pdf: bytes) -> io.BytesIO:
    return io.BytesIO(valid_pdf)


@pytest.fixture()
def corrupt_pdf_stream(corrupt_pdf: bytes) -> io.BytesIO:
    return io.BytesIO(corrupt_pdf)


@pytest.fixture()
def fake_pdf_text_stream(fake_pdf_text: bytes) -> io.BytesIO:
    return io.BytesIO(fake_pdf_text)


@pytest.fixture()
def oversize_pdf_stream(oversize_pdf: bytes) -> io.BytesIO:
    return io.BytesIO(oversize_pdf)