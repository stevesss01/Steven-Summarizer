import io

import pytest

pytest.importorskip("reportlab")
pdfplumber = pytest.importorskip("pdfplumber")

from app.services.pdf_export import render_report_pdf  # noqa: E402

REPORT = """# Resume Analysis

**Candidate:** Jane Doe · **Target role:** Data Analyst

## ATS Score: 72/100
| Criterion | Score | Note |
| --- | --- | --- |
| Skills and keywords | 18/25 | SQL, Python present |

## Bullet Rewrites
1. **Before:** Did reports
   **After:** Automated weekly reporting in Python, saving [N] hours
"""


def text_of(pdf: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf)) as doc:
        return "\n".join(page.extract_text() or "" for page in doc.pages)


def test_renders_headings_tables_and_lists():
    pdf = render_report_pdf(REPORT, title="Resume Review", source_name="cv.pdf")
    assert pdf.startswith(b"%PDF")
    text = text_of(pdf)
    for expected in ("Resume Analysis", "ATS SCORE: 72/100", "Skills and keywords", "Page 1 of 1"):
        assert expected in text


def test_unsupported_characters_do_not_break_rendering():
    pdf = render_report_pdf("# T\n\n- value ≤ 5 → ok ✓ 日本", title="X")
    assert "value <= 5 -> ok" in text_of(pdf)


def test_long_reports_paginate():
    body = "\n\n".join(f"## Section {i}\n- point {i}" for i in range(80))
    pdf = render_report_pdf("# Long\n\n" + body, title="Long")
    assert "Page 1 of" in text_of(pdf)
