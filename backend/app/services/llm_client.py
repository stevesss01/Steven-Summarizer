"""Async Groq client with key rotation, retries and model fallback."""

from __future__ import annotations

import asyncio
import itertools
import logging
import random
from dataclasses import dataclass
from typing import Any

from groq import AsyncGroq

from app.core.config import settings
from app.services.prompts import Message

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = frozenset({408, 409, 429, 500, 502, 503, 504})
MAX_RETRY_AFTER_S = 20.0
# Extra completion budget for reasoning models, whose hidden reasoning tokens
# count against the limit. Without it, short calls can return empty content.
REASONING_TOKEN_HEADROOM = 1500


class LLMServiceError(RuntimeError):
    """No model/key combination produced a usable response."""


class ContextTooLongError(LLMServiceError):
    """The request exceeded the model's context window."""


@dataclass(frozen=True)
class Completion:
    text: str
    model: str


def _status_code(exc: Exception) -> int | None:
    status = getattr(exc, "status_code", None)
    return status if isinstance(status, int) else None


def _retry_after(exc: Exception) -> float | None:
    headers = getattr(getattr(exc, "response", None), "headers", None)
    try:
        return min(float(headers["retry-after"]), MAX_RETRY_AFTER_S) if headers else None
    except (KeyError, TypeError, ValueError):
        return None


def _is_context_error(exc: Exception) -> bool:
    if _status_code(exc) == 413:
        return True
    message = str(exc).lower()
    return "context" in message and ("length" in message or "too long" in message)


def _is_transient(exc: Exception) -> bool:
    status = _status_code(exc)
    # Connection errors and timeouts carry no status code.
    return status is None or status in RETRYABLE_STATUS


def _request_params(model: str, messages: list[Message], max_tokens: int | None) -> dict[str, Any]:
    params: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": settings.temperature,
    }
    reasoning = settings.is_reasoning_model(model)
    if reasoning:
        params["reasoning_effort"] = settings.reasoning_effort
        params["include_reasoning"] = False
    if max_tokens:
        budget = max_tokens + (REASONING_TOKEN_HEADROOM if reasoning else 0)
        params["max_completion_tokens"] = budget
    return params


class LLMClient:
    def __init__(self, api_keys: list[str]) -> None:
        if not api_keys:
            raise LLMServiceError("GROQ_API_KEY is not configured on the server.")
        self._clients = [
            AsyncGroq(api_key=key, timeout=settings.request_timeout_s, max_retries=0)
            for key in api_keys
        ]
        self._rotation = itertools.cycle(range(len(self._clients)))

    def _next_client(self) -> AsyncGroq:
        return self._clients[next(self._rotation)]

    async def complete(
        self, messages: list[Message], *, max_tokens: int | None = None
    ) -> Completion:
        last_error: Exception | None = None

        for model in settings.models:
            for attempt in range(1, settings.max_retries + 1):
                params = _request_params(model, messages, max_tokens)

                try:
                    response = await self._next_client().chat.completions.create(**params)
                    content = response.choices[0].message.content
                    if not content or not content.strip():
                        raise LLMServiceError("empty response")
                    return Completion(text=content, model=model)
                except Exception as exc:
                    last_error = exc
                    if _is_context_error(exc):
                        raise ContextTooLongError(str(exc)) from exc
                    if not _is_transient(exc) or attempt == settings.max_retries:
                        break

                    delay = _retry_after(exc) or 0.75 * 2 ** (attempt - 1)
                    delay += random.uniform(0, 0.5)
                    logger.info(
                        "llm.retry model=%s attempt=%d error=%s delay=%.1fs",
                        model,
                        attempt,
                        type(exc).__name__,
                        delay,
                    )
                    await asyncio.sleep(delay)

            logger.warning("llm.fallback from_model=%s error=%s", model, last_error)

        raise LLMServiceError(
            "The AI service is busy right now. Please try again in a moment."
        ) from last_error


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient(settings.groq_api_keys)
    return _client
