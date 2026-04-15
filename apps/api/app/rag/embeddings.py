from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from app.core.config import Settings, get_settings


@lru_cache
def _client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def embed_texts(texts: list[str], settings: Settings | None = None) -> list[list[float]]:
    settings = settings or get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    client = _client(settings.openai_api_key)
    resp = client.embeddings.create(model=settings.embedding_model, input=texts)
    return [d.embedding for d in sorted(resp.data, key=lambda x: x.index)]
