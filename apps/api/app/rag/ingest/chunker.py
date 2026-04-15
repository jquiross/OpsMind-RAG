from __future__ import annotations

from dataclasses import dataclass

import tiktoken

from app.core.config import get_settings


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    token_count: int
    metadata: dict


def chunk_text(
    text: str,
    *,
    doc_metadata: dict | None = None,
    encoding_name: str = "cl100k_base",
) -> list[TextChunk]:
    settings = get_settings()
    enc = tiktoken.get_encoding(encoding_name)
    target = settings.chunk_target_tokens
    overlap = settings.chunk_overlap_tokens
    tokens = enc.encode(text)
    if not tokens:
        return []

    chunks: list[TextChunk] = []
    start = 0
    idx = 0
    while start < len(tokens):
        end = min(start + target, len(tokens))
        slice_tokens = tokens[start:end]
        content = enc.decode(slice_tokens)
        meta = {"section": doc_metadata.get("section") if doc_metadata else None}
        if doc_metadata:
            meta.update({k: v for k, v in doc_metadata.items() if k != "section"})
        chunks.append(
            TextChunk(
                chunk_index=idx,
                content=content,
                token_count=len(slice_tokens),
                metadata={k: v for k, v in meta.items() if v is not None},
            )
        )
        idx += 1
        if end >= len(tokens):
            break
        start = max(0, end - overlap)
    return chunks
