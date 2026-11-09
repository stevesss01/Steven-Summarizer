"""Application settings loaded from environment variables."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _api_keys() -> list[str]:
    """Support several keys (GROQ_API_KEYS) so load is spread across them."""
    keys = _split_csv(os.getenv("GROQ_API_KEYS", ""))
    single = os.getenv("GROQ_API_KEY")
    if single and single not in keys:
        keys.append(single)
    return keys


@dataclass(frozen=True)
class Settings:
    app_name: str = "Steven-Summarizer API"
    version: str = "2.0.0"

    # --- LLM -------------------------------------------------------------
    groq_api_keys: list[str] = field(default_factory=_api_keys)
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    # Tried in order when the primary model is rate-limited or failing.
    fallback_models: list[str] = field(
        default_factory=lambda: _split_csv(
            os.getenv("GROQ_FALLBACK_MODELS", "llama-3.1-8b-instant")
        )
    )
    temperature: float = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
    request_timeout_s: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

    # --- Long-document handling -----------------------------------------
    # Documents up to this size are analysed in a single request.
    single_pass_chars: int = int(os.getenv("SINGLE_PASS_CHARS", "12000"))
    # Longer documents are split into sections of roughly this size.
    chunk_chars: int = int(os.getenv("CHUNK_CHARS", "8000"))
    chunk_overlap_chars: int = int(os.getenv("CHUNK_OVERLAP_CHARS", "400"))
    # Sections analysed at the same time (keeps within provider rate limits).
    max_concurrency: int = int(os.getenv("MAX_CONCURRENCY", "3"))
    # Hard ceiling on text processed per request (~40-60 pages).
    max_document_chars: int = int(os.getenv("MAX_DOCUMENT_CHARS", "120000"))
    max_pages: int = int(os.getenv("MAX_PAGES", "200"))

    # --- Operations ----------------------------------------------------
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    # Analyses allowed per client IP per minute (0 disables the limit).
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    # --- Uploads & CORS -------------------------------------------------
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    allowed_origins: list[str] = field(
        default_factory=lambda: _split_csv(
            os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost:5173,https://steven-summarizer.vercel.app",
            )
        )
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def models(self) -> list[str]:
        ordered = [self.groq_model, *self.fallback_models]
        return list(dict.fromkeys(m for m in ordered if m))


settings = Settings()
