"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.summarize import router as summarize_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Upload a PDF and receive a structured AI-generated analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(summarize_router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Lightweight endpoint used by the frontend to wake the server."""
    return {"status": "ok"}
