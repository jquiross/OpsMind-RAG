# Evaluación offline

Dataset: `data/eval/eval_dataset.jsonl`.

Ejecución:

```bash
# desde la raíz, con Postgres y OPENAI_API_KEY configurados
python scripts/run_eval.py
```

Salida: `artifacts/eval_report.json` y `artifacts/eval_report.md`, y fila en `eval_runs`.

Métricas por estrategia: `hit_rate@k`, `precision@k`, MRR, latencias p50/p95.

Estrategias comparadas: `semantic_only`, `hybrid_rerank`, `bm25_only`, `hybrid_rerank_rewrite`.
