"""Split long text into overlapping sections on natural boundaries."""

from __future__ import annotations

_BOUNDARIES = ("\n\n", "\n", ". ", " ")


def split_text(text: str, chunk_chars: int, overlap_chars: int = 0) -> list[str]:
    """Return sections of at most ``chunk_chars`` characters.

    Cuts prefer paragraph breaks, then line breaks, then sentence ends, so a
    section rarely stops mid-sentence. A small overlap keeps context that spans
    a boundary from being lost.
    """
    text = text.strip()
    if chunk_chars <= 0:
        raise ValueError("chunk_chars must be positive")
    if len(text) <= chunk_chars:
        return [text] if text else []

    overlap_chars = max(0, min(overlap_chars, chunk_chars // 4))
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_chars, len(text))
        if end < len(text):
            window = text[start:end]
            # Only accept a boundary in the last 40% of the window.
            floor = int(len(window) * 0.6)
            for boundary in _BOUNDARIES:
                cut = window.rfind(boundary, floor)
                if cut != -1:
                    end = start + cut + len(boundary)
                    break

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap_chars, start + 1)

    return chunks
