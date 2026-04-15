from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.query import Feedback, Query, RetrievalResult


def dashboard_summary(db: Session) -> dict:
    total_queries = db.scalar(select(func.count()).select_from(Query)) or 0
    low_conf = db.scalar(
        select(func.count()).select_from(Query).where(Query.insufficient_evidence.is_(True))
    ) or 0
    feedback_rows = db.scalars(select(Feedback)).all()
    pos = sum(1 for f in feedback_rows if f.rating > 0)
    neg = sum(1 for f in feedback_rows if f.rating < 0)
    recent = db.scalars(select(Query).order_by(Query.created_at.desc()).limit(10)).all()
    chunk_usage = db.execute(
        select(RetrievalResult.chunk_id, func.count())
        .group_by(RetrievalResult.chunk_id)
        .order_by(func.count().desc())
        .limit(5)
    ).all()
    doc_titles: dict[UUID, str] = {}
    if chunk_usage:
        from app.models.document import DocumentChunk

        chunk_ids = [c[0] for c in chunk_usage]
        chunks = db.scalars(select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))).all()
        doc_ids = {c.document_id for c in chunks}
        docs = db.scalars(select(Document).where(Document.id.in_(doc_ids))).all()
        doc_titles = {d.id: d.title for d in docs}
        top_docs = []
        for cid, cnt in chunk_usage:
            ch = next((x for x in chunks if x.id == cid), None)
            if ch:
                top_docs.append({"document_title": doc_titles.get(ch.document_id, "?"), "hits": cnt})
    else:
        top_docs = []

    return {
        "total_queries": total_queries,
        "insufficient_evidence_queries": low_conf,
        "feedback_positive": pos,
        "feedback_negative": neg,
        "recent_queries": [
            {
                "id": str(q.id),
                "question": q.user_question[:200],
                "confidence": q.confidence,
                "created_at": q.created_at.isoformat(),
            }
            for q in recent
        ],
        "top_documents": top_docs,
    }
