from app.rag.ingest.chunker import chunk_text


def test_chunker_splits_long_text():
    text = "word " * 10000
    chunks = chunk_text(text, doc_metadata={"source_type": "txt"})
    assert len(chunks) >= 2
    assert all(c.token_count > 0 for c in chunks)


def test_chunker_empty():
    assert chunk_text("") == []
