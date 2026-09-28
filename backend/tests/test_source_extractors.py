from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.sources.extractors import (
    SourceExtractionError,
    decode_text,
    extract_pdf,
    validate_remote_url,
)


def test_text_decoder_accepts_utf8() -> None:
    assert decode_text("目标 → 流程".encode()) == "目标 → 流程"


def test_blank_text_is_rejected() -> None:
    with pytest.raises(SourceExtractionError, match="no readable text"):
        decode_text(b"   ")


def test_pdf_without_text_is_actionable_failure() -> None:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(buffer)
    with pytest.raises(SourceExtractionError, match="no extractable text"):
        extract_pdf(buffer.getvalue())


@pytest.mark.parametrize(
    "url", ["file:///etc/passwd", "http://localhost:8000", "ftp://example.com"]
)
def test_unsafe_url_is_rejected(url: str) -> None:
    with pytest.raises(SourceExtractionError):
        validate_remote_url(url)
