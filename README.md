# OpsMind RAG

**OpsMind RAG** is a full-stack application aimed at **enterprise-style technical support and incident handling**. It combines retrieval-augmented generation (**RAG**) with **hybrid search** (semantic + lexical), answers **grounded in internal documentation** with **verifiable citations**, **severity** classification and **triage** (when a human needs to step in), logging of **queries and feedback**, and an **offline evaluation harness** to measure retrieval quality and latency.

The goal is a knowledge and support system that feels **serious and demo-ready** (portfolio or MVP)—not a bare-bones “chat with PDFs” with no traceability.

---

## What the system does

| Area | Description |
|------|-------------|
| **Ingestion** | Indexes runbooks, FAQs, technical docs, and tickets (TXT, Markdown, PDF, JSON) into chunks with metadata and embeddings. |
| **Querying** | Accepts natural-language questions, optionally **rewrites the query** for better retrieval, pulls context with **pgvector** (similarity) and **BM25** (lexical), merges results, and generates a **structured** answer with the language model. |
| **Traceability** | Responses include **citations** tied to specific chunks; if evidence is thin, the system says so and avoids fabricating answers. |
| **Triage** | Estimates **severity** (e.g. low → critical), whether the case **needs a human**, and suggests **next steps**, using rules and the LLM where appropriate. |
| **Analytics** | Persists questions, retrieval traces, latencies, and **feedback** (helpful / not helpful) to power the metrics dashboard. |
| **Evaluation** | Offline evaluation script with a JSONL dataset: metrics such as hit@k, precision@k, MRR, p50/p95 latency, and comparison across retrieval **strategies**. |
| **Async processing** | **Celery** + **Redis** for background ingestion jobs when the worker is running. |

---

## Typical use cases

- Answer from **internal documentation** (runbooks, policies, procedures).
- Suggest **likely causes** and **resolution steps** for failures (auth, billing, integrations).
- Surface **evidence and sources** for audits or escalation.
- Flag **low-confidence** queries or incidents that should **escalate** to engineering or another team.

---

## Architecture (overview)

```
[ Next.js ] ──HTTP──▶ [ FastAPI ]
                         ├── Chat (rewrite → retrieve → generate → triage)
                         ├── Ingestion (parse → chunk → embed → persist)
                         ├── Analytics (queries, traces, feedback)
                         └── Evaluation (dataset, metrics, reports)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        PostgreSQL       Redis          Celery worker
        + pgvector      (broker)        (async ingestion)
```

- **Hybrid retrieval**: semantic and BM25 results are merged (RRF-style fusion + weighted scoring) and ranked for the context passed to the LLM.
- **Basic guardrails**: input sanitization, size limits, and prompts that treat retrieved context as **data**, not as user instructions.

More detail: [docs/architecture.md](docs/architecture.md).

---

## Tech stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, TypeScript, React, Tailwind CSS, shadcn/ui, TanStack Query |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| **Data** | PostgreSQL 16, **pgvector** extension, Redis |
| **Jobs** | Celery |
| **RAG / ML** | OpenAI (embeddings + chat), rank-bm25, tiktoken, pypdf |

---

## Repository layout

| Path | Contents |
|------|----------|
| `apps/api/` | FastAPI app, models, RAG services, Alembic, tests |
| `apps/web/` | Next.js UI (chat, ingestion, dashboard, evaluation) |
| `data/sample_docs/` | Sample documents for demos and seeds |
| `data/eval/` | JSONL dataset for offline evaluation |
| `scripts/` | `seed_demo_data.py`, `reindex.py`, `run_eval.py` |
| `docs/` | Architecture, ingestion, retrieval, evaluation, ADRs |

---

## Prerequisites

- **Docker** and **Docker Compose** (recommended to run the full stack).
- An **OpenAI** API key (`OPENAI_API_KEY`) for embeddings and answer generation.

---

## Quick start (Docker)

1. **Environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at least `OPENAI_API_KEY`, and Postgres/Redis credentials if you change them from the example.

2. **Start services** (Postgres, Redis, API, worker, web):

   ```bash
   docker compose up --build
   ```

   The API runs Alembic migrations on startup.

3. **Demo data** (optional—creates sample documents with embeddings):

   ```bash
   docker compose exec api python scripts/seed_demo_data.py
   ```

4. **URLs**

   | Service | Default URL |
   |---------|-------------|
   | Web UI | http://localhost:3000 |
   | REST API | http://localhost:8000 |
   | Interactive API docs (OpenAPI) | http://localhost:8000/docs |

---

## Local development without Docker (reference)

- **Backend:** Python 3.12, `cd apps/api`, install `requirements/dev.txt`, set `.env` with `POSTGRES_HOST=localhost`, run `alembic upgrade head`, then `uvicorn app.main:app --reload`.
- **Frontend:** `cd apps/web`, `npm ci`, `npm run dev` (set `NEXT_PUBLIC_API_URL` to the API base URL).

---

## Scripts

| Command | Purpose |
|---------|---------|
| `make dev` | Same as `docker compose up --build`. |
| `python scripts/seed_demo_data.py` | Loads sample documents with stable IDs (pairs well with the eval dataset). |
| `python scripts/reindex.py` | Rebuilds chunks and embeddings for existing documents. |
| `python scripts/run_eval.py` | Runs offline evaluation; writes reports under `artifacts/` and stores a run in the database. |

---

## Tests and quality

| Scope | Command |
|-------|---------|
| API unit tests | `cd apps/api && pytest -m "not integration"` |
| Frontend lint / build | `cd apps/web && npm run lint && npm run build` |
| E2E (Playwright) | `cd apps/web && npm run test:e2e` |

CI: [.github/workflows/ci.yml](.github/workflows/ci.yml).

---

## Further documentation

- [Architecture](docs/architecture.md) — overview and diagram.
- [Ingestion](docs/ingestion.md) — formats and pipeline.
- [Retrieval](docs/retrieval.md) — semantic, BM25, and hybrid strategies.
- [Evaluation](docs/evaluation.md) — metrics and running the eval harness.
- [API examples](docs/api_examples.md) — sample payloads.
- [Demo script](docs/demo_script.md) — suggested demo steps.
- [ADRs](docs/decisions/) — short design decisions.

---

## License

Reference / portfolio project—add whichever license fits your use case (MIT, proprietary, etc.).
