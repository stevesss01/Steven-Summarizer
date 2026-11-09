"""Wrapper around the Groq chat completions API."""

from functools import lru_cache

from groq import Groq

from app.core.config import settings
from app.services.prompts import AnalysisMode, build_prompt


class LLMServiceError(RuntimeError):
    """Raised when the language model cannot produce a response."""


@lru_cache(maxsize=1)
def _get_client() -> Groq:
    if not settings.groq_api_key:
        raise LLMServiceError("GROQ_API_KEY is not configured on the server.")
    return Groq(api_key=settings.groq_api_key)


def generate_summary(text: str, mode: AnalysisMode) -> str:
    """Send the document text to the model and return a markdown analysis."""
    prompt = build_prompt(mode, text[: settings.max_input_chars])

    try:
        response = _get_client().chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.temperature,
        )
    except LLMServiceError:
        raise
    except Exception as exc:  # network / API errors from the SDK
        raise LLMServiceError("The AI service is unavailable. Please try again.") from exc

    content = response.choices[0].message.content
    if not content:
        raise LLMServiceError("The AI service returned an empty response.")
    return content
