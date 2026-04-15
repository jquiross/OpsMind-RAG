"""Offline retrieval evaluation; writes JSON/Markdown and stores EvalRun."""
from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

for path in (REPO_ROOT / "apps" / "api", REPO_ROOT):
    if (path / "app").is_dir():
        sys.path.insert(0, str(path))
        break

os.environ.setdefault("POSTGRES_HOST", "localhost")

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.eval_run import EvalRun
from app.rag.embeddings import embed_texts
from app.rag.eval.metrics import hit_at_k, mean_reciprocal_rank, percentile, precision_at_k
from app.rag.eval.runner import build_report, load_dataset
from app.rag.retrieve.hybrid import HybridRetriever
from app.services.query_rewrite import rewrite_query_for_search


def run_strategy(
    db: Session,
    rows: list[dict],
    strategy: str,
    k: int,
) -> dict:
    settings = get_settings()
    latencies: list[float] = []
    hits = 0
    precs: list[float] = []
    mrrs: list[float] = []
    for row in rows:
        original_q = row["question"]
        q_text = original_q
        if strategy == "hybrid_rerank_rewrite":
            q_text = rewrite_query_for_search(original_q, settings)
        t0 = time.perf_counter()
        emb = embed_texts([q_text], settings)[0]
        retr = HybridRetriever(db, settings)
        map_strategy = "hybrid_rerank"
        if strategy == "semantic_only":
            map_strategy = "semantic_only"
        elif strategy == "bm25_only":
            map_strategy = "bm25_only"
        chunks = retr.retrieve(q_text, emb, top_k=k, strategy=map_strategy)
        latencies.append((time.perf_counter() - t0) * 1000)
        expected = [uuid.UUID(x) for x in row.get("expected_doc_ids", [])]
        retrieved_docs = [c.document_id for c in chunks]
        if expected:
            hits += int(hit_at_k(expected, retrieved_docs, k))
            precs.append(precision_at_k(expected, retrieved_docs, k))
            mrrs.append(mean_reciprocal_rank(expected, retrieved_docs))
    n = len(rows) or 1
    return {
        f"hit_rate@{k}": hits / n,
        f"precision@{k}": sum(precs) / len(precs) if precs else 0.0,
        "mrr": sum(mrrs) / len(mrrs) if mrrs else 0.0,
        "latency_p50_ms": percentile(latencies, 50),
        "latency_p95_ms": percentile(latencies, 95),
    }


def main() -> None:
    dataset = REPO_ROOT / "data" / "eval" / "eval_dataset.jsonl"
    out_dir = REPO_ROOT / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_dataset(dataset)
    db = SessionLocal()
    try:
        strategies = ["semantic_only", "hybrid_rerank", "bm25_only", "hybrid_rerank_rewrite"]
        comparison: dict[str, dict] = {}
        for s in strategies:
            comparison[s] = run_strategy(db, rows, s, k=5)
        build_report(comparison, out_dir / "eval_report.json", out_dir / "eval_report.md", k=5)
        er = EvalRun(
            name="offline_retrieval",
            dataset_name="eval_dataset.jsonl",
            metrics_json=comparison,
        )
        db.add(er)
        db.commit()
        print(json.dumps(comparison, indent=2))
        print(f"Wrote {out_dir / 'eval_report.json'}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
