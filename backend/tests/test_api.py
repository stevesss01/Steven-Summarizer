"""HTTP-level tests. The AI pipeline is replaced with a stub."""

import pytest

pytest.importorskip("fastapi")
fitz = pytest.importorskip("fitz")

from fastapi.testclient import TestClient  # noqa: E402

from app.api import summarize as summarize_module  # noqa: E402
from app.main import app  # noqa: E402
from app.services.summarizer import AnalysisResult  # noqa: E402

client = TestClient(app)


def make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture(autouse=True)
def stub_analysis(monkeypatch):
    async def fake(text, mode):
        return AnalysisResult(summary=f"# Report\n\n{mode.value}", models=["stub"])

    monkeypatch.setattr(summarize_module, "analyse_document", fake)


def post(data: bytes, name="doc.pdf", ctype="application/pdf", mode="general"):
    return client.post(
        "/summarize",
        files={"file": (name, data, ctype)},
        data={"mode": mode},
        headers={"x-forwarded-for": f"test-{name}-{mode}"},
    )


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_summarize_success():
    res = post(make_pdf("Quarterly revenue grew 12 percent."), mode="resume")
    assert res.status_code == 200
    body = res.json()
    assert body["mode"] == "resume"
    assert body["summary"].startswith("# Report")
    assert body["meta"]["pages"] == 1
    assert "X-Request-ID" in res.headers


def test_rejects_non_pdf():
    assert post(b"hello", name="notes.txt", ctype="text/plain").status_code == 415


def test_rejects_corrupt_pdf():
    assert post(b"not really a pdf").status_code == 400


def test_rejects_pdf_without_text():
    assert post(make_pdf(""), name="blank.pdf").status_code == 422


def test_rejects_unknown_mode():
    assert post(make_pdf("text"), mode="poetry").status_code == 422
