from app.services.chunking import split_text


def test_short_text_is_single_chunk():
    assert split_text("hello world", 100) == ["hello world"]


def test_empty_text_returns_no_chunks():
    assert split_text("   ", 100) == []


def test_chunks_respect_size_and_cover_text():
    paragraphs = [f"Paragraph {i}. " + "word " * 60 for i in range(40)]
    text = "\n\n".join(paragraphs)
    chunks = split_text(text, 1000, 100)
    assert len(chunks) > 1
    assert all(len(c) <= 1000 for c in chunks)
    for i in range(40):
        assert any(f"Paragraph {i}." in c for c in chunks)


def test_prefers_paragraph_boundaries():
    text = ("a" * 700) + "\n\n" + ("b" * 700)
    chunks = split_text(text, 1000, 0)
    assert chunks[0] == "a" * 700
    assert chunks[1] == "b" * 700


def test_unbroken_text_still_terminates():
    chunks = split_text("x" * 5000, 1000, 200)
    assert all(len(c) <= 1000 for c in chunks)
    assert len(chunks) >= 5
