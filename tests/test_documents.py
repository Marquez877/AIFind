from app.infrastructure.ai.embedding_service import chunk_text


def test_chunk_text_splits_large_text_with_overlap():
    text = ("Предложение. " * 200).strip()
    chunks = chunk_text(text, chunk_size=120, overlap=20)

    assert len(chunks) > 1
    assert all(chunks)
    assert all(len(chunk) <= 140 for chunk in chunks)


def test_chunk_text_returns_empty_for_blank_input():
    assert chunk_text("   ") == []
