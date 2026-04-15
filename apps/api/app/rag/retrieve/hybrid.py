from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.document import Document, DocumentChunk


@dataclass
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    document_title: str
    content: str
    score: float
    retrieval_type: str


def tokenize_query(q: str) -> list[str]:
    return [t for t in re.split(r"\W+", q.lower()) if t]


def cosine_distance_to_score(distance: float) -> float:
    return max(0.0, 1.0 - float(distance) / 2.0)


class HybridRetriever:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()

    def semantic_search(self, embedding: list[float], limit: int) -> list[tuple[DocumentChunk, float]]:
        distance_expr = DocumentChunk.embedding.cosine_distance(embedding)
        q = (
            select(DocumentChunk, distance_expr.label("dist"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance_expr)
            .limit(limit)
        )
        rows = self.db.execute(q).all()
        out: list[tuple[DocumentChunk, float]] = []
        for chunk, dist in rows:
            score = cosine_distance_to_score(float(dist))
            out.append((chunk, score))
        return out

    def bm25_search(self, query: str, limit: int) -> list[tuple[DocumentChunk, float]]:
        chunks = self.db.scalars(
            select(DocumentChunk).where(DocumentChunk.embedding.is_not(None))
        ).all()
        if not chunks:
            return []
        corpus = [tokenize_query(c.content) for c in chunks]
        bm25 = BM25Okapi(corpus)
        q_tokens = tokenize_query(query)
        scores = bm25.get_scores(q_tokens)
        ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:limit]
        max_score = max((scores[i] for i in ranked), default=1.0) or 1.0
        out: list[tuple[DocumentChunk, float]] = []
        for i in ranked:
            norm = float(scores[i]) / max_score if max_score else 0.0
            out.append((chunks[i], norm))
        return out

    def reciprocal_rank_fusion(
        self,
        lists: list[list[tuple[DocumentChunk, float]]],
        k: int = 60,
    ) -> dict[UUID, float]:
        scores: dict[UUID, float] = {}
        for lst in lists:
            for rank, (chunk, _) in enumerate(lst, start=1):
                cid = chunk.id
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
        return scores

    def retrieve(
        self,
        query: str,
        query_embedding: list[float],
        top_k: int | None = None,
        strategy: str = "hybrid_rerank",
    ) -> list[RetrievedChunk]:
        top_k = top_k or self.settings.retrieval_top_k
        sem_limit = max(top_k * 3, top_k)
        lex_limit = max(top_k * 3, top_k)

        semantic = self.semantic_search(query_embedding, sem_limit)
        lexical = self.bm25_search(query, lex_limit)

        if strategy == "semantic_only":
            return self._to_chunks(semantic[:top_k], "semantic")

        if strategy == "bm25_only":
            return self._to_chunks(lexical[:top_k], "bm25")

        rrf = self.reciprocal_rank_fusion([semantic, lexical])
        chunk_by_id: dict[UUID, DocumentChunk] = {}
        for ch, _ in semantic + lexical:
            chunk_by_id[ch.id] = ch

        ordered_ids = sorted(rrf.keys(), key=lambda cid: rrf[cid], reverse=True)[: top_k * 2]

        reranked: list[tuple[DocumentChunk, float, str]] = []
        w_sem = self.settings.hybrid_semantic_weight
        w_lex = 1.0 - w_sem
        for cid in ordered_ids:
            ch = chunk_by_id.get(cid)
            if not ch:
                continue
            sem_score = next((s for c, s in semantic if c.id == cid), 0.0)
            lex_score = next((s for c, s in lexical if c.id == cid), 0.0)
            hybrid_score = w_sem * sem_score + w_lex * lex_score
            reranked.append((ch, hybrid_score, "hybrid"))

        reranked.sort(key=lambda x: x[1], reverse=True)
        final = reranked[:top_k]
        doc_titles = {d.id: d.title for d in self.db.scalars(select(Document)).all()}
        out: list[RetrievedChunk] = []
        for ch, score, rtype in final:
            out.append(
                RetrievedChunk(
                    chunk_id=ch.id,
                    document_id=ch.document_id,
                    document_title=doc_titles.get(ch.document_id, "Unknown"),
                    content=ch.content,
                    score=score,
                    retrieval_type=rtype,
                )
            )
        return out

    def _to_chunks(self, rows: list[tuple[DocumentChunk, float]], rtype: str) -> list[RetrievedChunk]:
        doc_ids = {c.document_id for c, _ in rows}
        titles: dict[UUID, str] = {}
        if doc_ids:
            docs = self.db.scalars(select(Document).where(Document.id.in_(doc_ids))).all()
            titles = {d.id: d.title for d in docs}
        return [
            RetrievedChunk(
                chunk_id=c.id,
                document_id=c.document_id,
                document_title=titles.get(c.document_id, "Unknown"),
                content=c.content,
                score=s,
                retrieval_type=rtype,
            )
            for c, s in rows
        ]
