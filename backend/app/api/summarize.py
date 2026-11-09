"""Summarisation endpoint."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.rate_limit import enforce_rate_limit
from app.services.llm_client import LLMServiceError
from app.services.pdf_service import PDFExtractionError, extract_text_async
from app.services.prompts import AnalysisMode
from app.services.summarizer import analyse_document

router = APIRouter(tags=["analysis"])


@router.post("/summarize", dependencies=[Depends(enforce_rate_limit)])
async def summarize_pdf(
    file: Annotated[UploadFile, File(description="PDF document to analyse")],
    mode: Annotated[AnalysisMode, Form(description="Type of analysis")] = AnalysisMode.GENERAL,
) -> dict:
    """Extract text from an uploaded PDF and return an AI-generated analysis."""
    started = time.perf_counter()

    filename = (file.filename or "").lower()
    if file.content_type != "application/pdf" and not filename.endswith(".pdf"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF files are supported.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File is larger than {settings.max_upload_mb} MB.",
        )

    try:
        extracted = await extract_text_async(pdf_bytes, settings.max_pages)
    except PDFExtractionError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    if not extracted.text.strip():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "No readable text found. Scanned PDFs are not supported yet.",
        )

    try:
        result = await analyse_document(extracted.text, mode)
    except LLMServiceError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    return {
        "summary": result.summary,
        "mode": mode.value,
        "meta": {
            "pages": extracted.pages,
            "pages_analysed": extracted.pages_read,
            "sections": result.sections,
            "truncated": result.truncated or extracted.pages_read < extracted.pages,
            "models": result.models,
            "seconds": round(time.perf_counter() - started, 1),
        },
    }
