from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.rag.embeddings import embed_texts
from app.rag.eval.metrics import (
    citation_coverage,
    groundedness_proxy,
    hit_at_k,
    mean_reciprocal_rank,
    percentile,
    precision_at_k,
)
from app.rag.retrieve.hybrid import HybridRetriever


def load_dataset(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def run_retrieval_eval(
    db: Session,
    dataset_path: Path,
    strategies: list[str],
    k: int = 5,
) -> dict:
    settings = get_settings()
    data = load_dataset(dataset_path)
    results: dict[str, dict] = {}
    for strategy in strategies:
        latencies: list[float] = []
        hits = 0
        precs: list[float] = []
        mrrs: list[float] = []
        for row in data:
            q = row["question"]
            expected = [UUID(x) for x in row.get("expected_doc_ids", [])]
            t0 = time.perf_counter()
            emb = embed_texts([q], settings)[0]
            retr = HybridRetriever(db, settings)
            chunks = retr.retrieve(q, emb, top_k=k, strategy=strategy)
            latencies.append((time.perf_counter() - t0) * 1000)
            retrieved_docs = [c.document_id for c in chunks]
            if expected:
                hits += int(hit_at_k(expected, retrieved_docs, k))
                precs.append(precision_at_k(expected, retrieved_docs, k))
                mrrs.append(mean_reciprocal_rank(expected, retrieved_docs))
        n = len(data) or 1
        results[strategy] = {
            f"hit_rate@{k}": hits / n,
            f"precision@{k}": float(statistics.mean(precs)) if precs else 0.0,
            "mrr": float(statistics.mean(mrrs)) if mrrs else 0.0,
            "latency_p50_ms": percentile(latencies, 50),
            "latency_p95_ms": percentile(latencies, 95),
        }
    return results


def build_report(comparison: dict, output_json: Path, output_md: Path, k: int = 5) -> None:
    output_json.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    lines = [
        "# Eval report",
        "",
        f"| Strategy | hit@{k} | precision@{k} | MRR | p50 ms | p95 ms |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    hk = f"hit_rate@{k}"
    pk = f"precision@{k}"
    for name, m in comparison.items():
        lines.append(
            f"| {name} | {m.get(hk, 0):.3f} | {m.get(pk, 0):.3f} | "
            f"{m.get('mrr', 0):.3f} | {m.get('latency_p50_ms', 0):.1f} | {m.get('latency_p95_ms', 0):.1f} |"
        )
    output_md.write_text("\n".join(lines), encoding="utf-8")
