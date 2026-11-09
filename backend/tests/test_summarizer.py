"""Pipeline tests using a fake LLM client (no network or API key needed)."""

import asyncio

import pytest

from app.core.config import settings
from app.services.llm_client import Completion, ContextTooLongError, LLMServiceError
from app.services.prompts import AnalysisMode
from app.services.summarizer import Summarizer, clean_report

REPORT = "# Final report\n\n## Overview\nA sufficiently long, well-formed markdown report body."


class FakeClient:
    def __init__(self, fail_sections=(), context_limit=None):
        self.calls = []
        self.fail_sections = set(fail_sections)
        self.context_limit = context_limit
        self.active = 0
        self.peak = 0

    async def complete(self, messages, *, max_tokens=None):
        system, user = messages[0]["content"], messages[1]["content"]
        prompt = system + user
        self.calls.append(messages)
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(0.01)
            if self.context_limit and len(prompt) > self.context_limit:
                raise ContextTooLongError("context length exceeded")
            for n in self.fail_sections:
                if user.startswith(f"Part {n} of"):
                    raise LLMServiceError("busy")
            if system.startswith("You extract notes"):
                return Completion(text="- note", model="fake-small")
            return Completion(text=REPORT, model="fake-large")
        finally:
            self.active -= 1


def long_text(chars):
    para = "Revenue grew 12% in 2025 according to the annual report. " * 10
    out = []
    while sum(len(p) for p in out) < chars:
        out.append(para)
    return "\n\n".join(out)


def run(coro):
    return asyncio.run(coro)


def test_short_document_uses_single_call():
    client = FakeClient()
    result = run(Summarizer(client).analyse("short doc", AnalysisMode.GENERAL))
    assert result.summary == REPORT
    assert result.sections == 1
    assert len(client.calls) == 1


def test_long_document_is_split_and_merged():
    client = FakeClient()
    result = run(Summarizer(client).analyse(long_text(60_000), AnalysisMode.RESEARCH))
    assert result.sections > 1
    section_calls = [m for m in client.calls if m[0]["content"].startswith("You extract notes")]
    assert len(section_calls) == result.sections
    assert result.summary == REPORT
    assert client.peak <= settings.max_concurrency * max(1, len(settings.groq_api_keys))


def test_failed_minority_of_sections_is_tolerated():
    client = FakeClient(fail_sections={2})
    result = run(Summarizer(client).analyse(long_text(60_000), AnalysisMode.GENERAL))
    assert result.summary == REPORT


def test_mostly_failed_sections_raise_clean_error():
    client = FakeClient(fail_sections=set(range(1, 50)))
    with pytest.raises(LLMServiceError):
        run(Summarizer(client).analyse(long_text(60_000), AnalysisMode.GENERAL))


def test_context_error_on_single_pass_falls_back_to_sections():
    client = FakeClient(context_limit=6_000)
    result = run(Summarizer(client).analyse(long_text(10_000), AnalysisMode.RESUME))
    assert result.sections > 1
    assert result.summary == REPORT


def test_oversized_document_is_truncated():
    client = FakeClient()
    result = run(
        Summarizer(client).analyse(
            long_text(settings.max_document_chars + 20_000), AnalysisMode.GENERAL
        )
    )
    assert result.truncated is True


def test_unusable_report_is_retried_once():
    class Flaky(FakeClient):
        async def complete(self, messages, *, max_tokens=None):
            self.calls.append(messages)
            text = "Sure!" if len(self.calls) == 1 else REPORT
            return Completion(text=text, model="fake")

    client = Flaky()
    result = run(Summarizer(client).analyse("short doc", AnalysisMode.GENERAL))
    assert result.summary == REPORT
    assert len(client.calls) == 2


def test_clean_report_strips_fences_and_preamble():
    raw = "```markdown\nHere is your report:\n# Title\n- point\n```"
    assert clean_report(raw) == "# Title\n- point"
