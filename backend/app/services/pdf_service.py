"""PDF text extraction using PyMuPDF."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import fitz  # PyMuPDF


class PDFExtractionError(ValueError):
    """Raised when a file cannot be read as a PDF."""


@dataclass
class ExtractedText:
    text: str
    pages: int
    pages_read: int


def extract_text(pdf_bytes: bytes, max_pages: int | None = None) -> ExtractedText:
    """Return the plain text of the PDF, reading at most ``max_pages`` pages."""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            total = pdf.page_count
            limit = total if max_pages is None else min(total, max_pages)
            text = "\n".join(pdf[i].get_text() for i in range(limit))
            return ExtractedText(text=text, pages=total, pages_read=limit)
    except Exception as exc:
        raise PDFExtractionError("The file could not be read as a PDF.") from exc


async def extract_text_async(pdf_bytes: bytes, max_pages: int | None = None) -> ExtractedText:
    """Run extraction in a worker thread so large PDFs don't block other requests."""
    return await asyncio.to_thread(extract_text, pdf_bytes, max_pages)
