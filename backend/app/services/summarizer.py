"""Document analysis pipeline.

Short documents are analysed in a single request. Longer ones are split into
sections, notes are extracted from the sections concurrently, and the notes are
merged into the final report (map-reduce). A failed section is skipped as long
as most of the document was processed.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.chunking import split_text
from app.services.llm_client import (
    ContextTooLongError,
    LLMClient,
    LLMServiceError,
    get_llm_client,
)
from app.services.prompts import AnalysisMode, build_messages, build_section_messages

logger = logging.getLogger(__name__)

MAX_REDUCE_ROUNDS = 3
SECTION_NOTE_TOKENS = 450
FINAL_REPORT_TOKENS = 1500
MIN_REPORT_CHARS = 80

_FENCE = re.compile(r"^```(?:markdown|md)?\s*\n(.*)\n```\s*$", re.DOTALL)


@dataclass
class AnalysisResult:
    summary: str
    sections: int = 1
    truncated: bool = False
    models: list[str] = field(default_factory=list)


def clean_report(text: str) -> str:
    """Strip code fences and any chatter before the first markdown heading."""
    text = text.strip()
    match = _FENCE.match(text)
    if match:
        text = match.group(1).strip()
    heading = text.find("#")
    if 0 < heading < 200:
        text = text[heading:]
    return text


_section_slots: dict[int, asyncio.Semaphore] = {}


def _section_semaphore() -> asyncio.Semaphore:
    """Process-wide cap on concurrent section calls, scaled by the number of API keys."""
    loop_id = id(asyncio.get_running_loop())
    if loop_id not in _section_slots:
        _section_slots.clear()
        slots = max(1, settings.max_concurrency) * max(1, len(settings.groq_api_keys))
        _section_slots[loop_id] = asyncio.Semaphore(slots)
    return _section_slots[loop_id]


class Summarizer:
    def __init__(self, client: LLMClient) -> None:
        self._client = client

    async def analyse(self, text: str, mode: AnalysisMode) -> AnalysisResult:
        text = text.strip()
        truncated = len(text) > settings.max_document_chars
        text = text[: settings.max_document_chars]

        if len(text) <= settings.single_pass_chars:
            try:
                summary, model = await self._final_report(mode, text, from_notes=False)
                return AnalysisResult(summary=summary, truncated=truncated, models=[model])
            except ContextTooLongError:
                logger.info("analysis.single_pass_too_long; using sections")

        return await self._analyse_in_sections(text, mode, truncated)

    async def _final_report(
        self, mode: AnalysisMode, text: str, *, from_notes: bool
    ) -> tuple[str, str]:
        messages = build_messages(mode, text, from_notes=from_notes)
        completion = await self._client.complete(messages, max_tokens=FINAL_REPORT_TOKENS)
        report = clean_report(completion.text)

        # Retry once if the model returned something unusable.
        if len(report) < MIN_REPORT_CHARS or not report.startswith("#"):
            completion = await self._client.complete(messages, max_tokens=FINAL_REPORT_TOKENS)
            report = clean_report(completion.text)
        return report, completion.model

    async def _analyse_in_sections(
        self, text: str, mode: AnalysisMode, truncated: bool
    ) -> AnalysisResult:
        chunks = split_text(text, settings.chunk_chars, settings.chunk_overlap_chars)
        models: set[str] = set()

        notes = await self._extract_notes(chunks, mode, models)
        combined = _join_notes(notes)

        rounds = 0
        while len(combined) > settings.single_pass_chars and rounds < MAX_REDUCE_ROUNDS:
            rounds += 1
            regrouped = split_text(combined, settings.chunk_chars)
            combined = _join_notes(await self._extract_notes(regrouped, mode, models))

        summary, model = await self._final_report(
            mode, combined[: settings.single_pass_chars], from_notes=True
        )
        models.add(model)
        return AnalysisResult(
            summary=summary, sections=len(chunks), truncated=truncated, models=sorted(models)
        )

    async def _extract_notes(
        self, chunks: list[str], mode: AnalysisMode, models: set[str]
    ) -> list[str]:
        total = len(chunks)
        semaphore = _section_semaphore()

        async def notes_for(text: str, index: int, max_tokens: int) -> str:
            completion = await self._client.complete(
                build_section_messages(mode, text, index, total), max_tokens=max_tokens
            )
            models.add(completion.model)
            return completion.text

        async def run(index: int, chunk: str) -> str | None:
            async with semaphore:
                try:
                    return await notes_for(chunk, index, SECTION_NOTE_TOKENS)
                except ContextTooLongError:
                    halves = split_text(chunk, max(len(chunk) // 2, 500))[:2]
                    parts = await asyncio.gather(
                        *(notes_for(h, index, SECTION_NOTE_TOKENS // 2) for h in halves),
                        return_exceptions=True,
                    )
                    return "\n".join(p for p in parts if isinstance(p, str)) or None
                except LLMServiceError as exc:
                    logger.warning("analysis.section_failed index=%d error=%s", index, exc)
                    return None

        results = await asyncio.gather(*(run(i, c) for i, c in enumerate(chunks, 1)))
        succeeded = [r for r in results if r]

        if len(succeeded) < max(1, (total + 1) // 2):
            raise LLMServiceError(
                "The AI service could not process enough of the document. "
                "Please try again in a moment."
            )
        if len(succeeded) < total:
            logger.warning(
                "analysis.sections_skipped skipped=%d total=%d", total - len(succeeded), total
            )
        return succeeded


def _join_notes(notes: list[str]) -> str:
    return "\n\n".join(f"### Part {i}\n{note.strip()}" for i, note in enumerate(notes, 1))


async def analyse_document(text: str, mode: AnalysisMode) -> AnalysisResult:
    return await Summarizer(get_llm_client()).analyse(text, mode)
