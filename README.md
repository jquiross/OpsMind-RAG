# OpsMind RAG

Asistente empresarial de soporte técnico e incidentes con **RAG**, recuperación **híbrida** (semántica + BM25), respuestas con **citas**, **triage** automático, analítica de consultas y **evaluación offline**.

## Stack

| Capa | Tecnología |
|------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui, TanStack Query |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic |
| Datos | PostgreSQL + pgvector, Redis |
| Jobs | Celery |
| RAG | OpenAI embeddings/LLM, rank-bm25, tiktoken, pypdf |

## Arranque local (Docker)

1. Copia variables: `cp .env.example .env` y define al menos `OPENAI_API_KEY` y credenciales de Postgres/Redis.
2. Desde la raíz del repo:

```bash
docker compose up --build
```

3. Migraciones se aplican al iniciar el servicio `api`. Semilla de demo (documentos de ejemplo + embeddings):

```bash
docker compose exec api python scripts/seed_demo_data.py
```

4. Interfaz: `http://localhost:3000` · API: `http://localhost:8000` · OpenAPI: `http://localhost:8000/docs`

## Comandos útiles

| Comando | Descripción |
|---------|-------------|
| `make dev` | `docker compose up --build` |
| `python scripts/run_eval.py` | Evaluación offline (requiere DB + `OPENAI_API_KEY`) |
| `python scripts/reindex.py` | Reindexa documentos existentes |

## Documentación

- [Arquitectura](docs/architecture.md)
- [Ingesta](docs/ingestion.md)
- [Recuperación](docs/retrieval.md)
- [Evaluación](docs/evaluation.md)
- [Ejemplos de API](docs/api_examples.md)
- [Demo](docs/demo_script.md)

## Tests y CI

- Backend: `cd apps/api && pytest -m "not integration"` (Python 3.12 + dependencias en `requirements/dev.txt`).
- Frontend: `cd apps/web && npm run lint && npm run build && npm run test:e2e`.
- GitHub Actions: [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Licencia

Uso educativo / portafolio; ajusta licencia según tu necesidad.
