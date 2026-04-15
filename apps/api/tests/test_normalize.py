from app.rag.ingest.normalize import normalize_text


def test_normalize_crlf():
    assert normalize_text("a\r\n\r\nb") == "a\n\nb"
