"""Application settings loaded from environment variables."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Steven-Summarizer API"
    version: str = "1.1.0"

    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    temperature: float = float(os.getenv("GROQ_TEMPERATURE", "0.3"))

    # Characters of extracted text sent to the model (keeps requests within context limits).
    max_input_chars: int = int(os.getenv("MAX_INPUT_CHARS", "12000"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))

    # Comma-separated list of frontend origins allowed to call the API.
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


settings = Settings()
