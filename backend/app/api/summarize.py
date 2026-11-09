"""Summarisation endpoint."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.services.groq_service import LLMServiceError, generate_summary
from app.services.pdf_service import PDFExtractionError, extract_text
from app.services.prompts import AnalysisMode

router = APIRouter(tags=["analysis"])


@router.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(..., description="PDF document to analyse"),
    mode: AnalysisMode = Form(AnalysisMode.GENERAL, description="Type of analysis"),
) -> dict[str, str]:
    """Extract text from an uploaded PDF and return an AI-generated analysis."""
    is_pdf = file.content_type == "application/pdf" or (file.filename or "").lower().endswith(".pdf")
    if not is_pdf:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF files are supported.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File is larger than {settings.max_upload_mb} MB.",
        )

    try:
        text = extract_text(pdf_bytes)
    except PDFExtractionError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    if not text.strip():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "No readable text found. Scanned PDFs are not supported yet.",
        )

    try:
        summary = generate_summary(text, mode)
    except LLMServiceError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    return {"summary": summary, "mode": mode.value}
