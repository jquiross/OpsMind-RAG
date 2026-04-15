from __future__ import annotations

import statistics
from dataclasses import dataclass
from uuid import UUID


@dataclass
class RetrievalEvalRow:
    question: str
    hit_at_k: bool
    precision_at_k: float
    reciprocal_rank: float
    latency_ms: float
    strategy: str


def hit_at_k(expected_doc_ids: list[UUID], retrieved_doc_ids: list[UUID], k: int) -> bool:
    top = retrieved_doc_ids[:k]
    return any(e in top for e in expected_doc_ids)


def precision_at_k(expected_doc_ids: list[UUID], retrieved_doc_ids: list[UUID], k: int) -> float:
    top = retrieved_doc_ids[:k]
    if not top:
        return 0.0
    hits = sum(1 for d in top if d in expected_doc_ids)
    return hits / len(top)


def mean_reciprocal_rank(expected_doc_ids: list[UUID], retrieved_doc_ids: list[UUID]) -> float:
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in expected_doc_ids:
            return 1.0 / rank
    return 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = max(0, min(len(values) - 1, int(round((p / 100) * (len(values) - 1)))))
    return values[k]


def citation_coverage(cited_chunk_ids: set[str], context_chunk_ids: set[str]) -> float:
    if not cited_chunk_ids:
        return 0.0
    valid = sum(1 for c in cited_chunk_ids if c in context_chunk_ids)
    return valid / len(cited_chunk_ids)


def groundedness_proxy(answer: str, context: str) -> float:
    """Simple lexical overlap ratio as a groundedness proxy."""
    a = set(answer.lower().split())
    c = set(context.lower().split())
    if not a:
        return 0.0
    return len(a & c) / len(a)
