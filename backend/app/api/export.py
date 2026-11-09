"""Report export endpoints."""

import re
from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.pdf_export import render_report_pdf

router = APIRouter(prefix="/export", tags=["export"])

MAX_REPORT_CHARS = 60_000


class ReportExport(BaseModel):
    markdown: str = Field(min_length=1, max_length=MAX_REPORT_CHARS)
    title: str = Field(default="Analysis Report", max_length=120)
    source_name: str | None = Field(default=None, max_length=255)


def _filename(source_name: str | None, title: str) -> str:
    base = re.sub(r"\.pdf$", "", source_name or "", flags=re.IGNORECASE) or title
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", f"{base}-{title}").strip("-").lower()
    return f"{slug[:100] or 'report'}.pdf"


@router.post("/pdf", response_class=Response)
async def export_pdf(report: Annotated[ReportExport, Body()]) -> Response:
    """Render a markdown report as a downloadable PDF."""
    pdf = await run_in_threadpool(
        render_report_pdf,
        report.markdown,
        title=report.title,
        source_name=report.source_name,
    )
    filename = _filename(report.source_name, report.title)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
