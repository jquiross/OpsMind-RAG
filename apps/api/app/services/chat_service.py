from __future__ import annotations

import json
import time
import uuid
from typing import Any
from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.query import Query, RetrievalResult
from app.rag.embeddings import embed_texts
from app.rag.prompts.chat_prompt import SYSTEM_PROMPT, USER_TEMPLATE, build_context_blocks
from app.rag.retrieve.hybrid import HybridRetriever
from app.schemas.chat import ChatResponse, CitationSchema, TriageSchema
from app.services.guardrails import detect_prompt_injection_signals, sanitize_user_text
from app.services.query_rewrite import rewrite_query_for_search
from app.services.triage import run_triage


def _empty_response(
    query_id: UUID,
    rewritten: str | None,
    triage_label: str,
    injection_signals: list[str],
) -> ChatResponse:
    triage = TriageSchema(
        severity="medium",
        needs_human=True,
        confidence=0.2,
        reasoning_summary="No indexed evidence available.",
        suggested_next_steps=["Ingest relevant runbooks", "Provide timestamps and error text"],
        label=triage_label,
    )
    return ChatResponse(
        summary="Not enough internal evidence to answer this question safely.",
        probable_cause="Insufficient or missing documentation in the index.",
        suggested_steps=[
            "Upload related runbooks or tickets",
            "Rephrase with product area and error codes",
        ],
        confidence=0.15,
        needs_human=True,
        severity="medium",
        citations=[],
        triage=triage,
        query_id=query_id,
        rewritten_query=rewritten,
        insufficient_evidence=True,
        injection_signals=injection_signals,
        raw_json=None,
    )


def run_chat(
    db: Session,
    question: str,
    retrieval_strategy: str = "hybrid_rerank",
    use_query_rewrite: bool = True,
) -> ChatResponse:
    settings = get_settings()
    t0 = time.perf_counter()
    clean = sanitize_user_text(question)
    injection_signals = detect_prompt_injection_signals(clean)

    rewritten = rewrite_query_for_search(clean, settings) if use_query_rewrite else clean
    embed_query = rewritten

    try:
        q_emb = embed_texts([embed_query], settings)[0]
    except Exception:
        q_emb = embed_texts([clean], settings)[0]

    retriever = HybridRetriever(db, settings)
    retrieved = retriever.retrieve(rewritten, q_emb, strategy=retrieval_strategy)
    max_score = max((r.score for r in retrieved), default=0.0)

    query_row = Query(
        user_question=clean,
        rewritten_query=rewritten,
    )
    db.add(query_row)
    db.flush()

    if not retrieved or max_score < settings.min_confidence_threshold:
        query_row.insufficient_evidence = True
        query_row.latency_ms = int((time.perf_counter() - t0) * 1000)
        query_row.response_text = json.dumps({"note": "insufficient_evidence"})
        db.commit()
        return _empty_response(query_row.id, rewritten, "no_evidence", injection_signals)

    chunks_for_prompt: list[tuple[str, str, str]] = [
        (str(r.chunk_id), r.document_title, r.content) for r in retrieved
    ]
    context = build_context_blocks(chunks_for_prompt)

    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured")

    user_msg = USER_TEMPLATE.format(context_blocks=context, question=clean)
    resp = client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw_text = resp.choices[0].message.content or "{}"
    data: dict[str, Any] = json.loads(raw_text)

    allowed_ids = {str(r.chunk_id) for r in retrieved}
    citations_raw = data.get("citations") or []
    citations: list[CitationSchema] = []
    for c in citations_raw:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("chunk_id", ""))
        if cid in allowed_ids:
            citations.append(
                CitationSchema(document_title=str(c.get("document_title", "")), chunk_id=cid)
            )

    conf = float(data.get("confidence", 0.5))
    if injection_signals:
        conf = min(conf, 0.6)

    summary = str(data.get("summary", ""))
    triage = run_triage(clean, summary, max(conf, max_score), settings)

    latency_ms = int((time.perf_counter() - t0) * 1000)

    response_model = ChatResponse(
        summary=summary,
        probable_cause=str(data.get("probable_cause", "")),
        suggested_steps=list(data.get("suggested_steps") or []),
        confidence=conf,
        needs_human=triage.needs_human,
        severity=triage.severity,
        citations=citations,
        triage=TriageSchema(
            severity=triage.severity,
            needs_human=triage.needs_human,
            confidence=triage.confidence,
            reasoning_summary=triage.reasoning_summary,
            suggested_next_steps=triage.suggested_next_steps,
            label=triage.label,
        ),
        query_id=query_row.id,
        rewritten_query=rewritten,
        insufficient_evidence=False,
        injection_signals=injection_signals,
        raw_json=data,
    )

    query_row.response_text = json.dumps(data)
    query_row.response_json = data
    query_row.confidence = conf
    query_row.triage_label = triage.label
    query_row.triage_json = {
        "severity": triage.severity,
        "needs_human": triage.needs_human,
        "confidence": triage.confidence,
        "reasoning_summary": triage.reasoning_summary,
        "suggested_next_steps": triage.suggested_next_steps,
        "label": triage.label,
    }
    query_row.latency_ms = latency_ms

    for rank, r in enumerate(retrieved, start=1):
        db.add(
            RetrievalResult(
                id=uuid.uuid4(),
                query_id=query_row.id,
                chunk_id=r.chunk_id,
                score=r.score,
                rank=rank,
                retrieval_type=r.retrieval_type,
            )
        )

    db.commit()
    return response_model
