"""PDF text extraction using PyMuPDF."""

import fitz  # PyMuPDF


class PDFExtractionError(ValueError):
    """Raised when a file cannot be read as a PDF."""


def extract_text(pdf_bytes: bytes) -> str:
    """Return the plain text of every page in the PDF."""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            return "\n".join(page.get_text() for page in pdf)
    except Exception as exc:
        raise PDFExtractionError("The file could not be read as a PDF.") from exc
