# OpsMind RAG

**OpsMind RAG** es una aplicación full stack orientada a **soporte técnico e incidentes en entornos empresariales**. Combina recuperación aumentada por generación (**RAG**) con **búsqueda híbrida** (semántica + léxica), respuestas **fundamentadas en documentación interna** con **citas verificables**, clasificación de **severidad** y **triage** (cuándo hace falta intervención humana), registro de **consultas y feedback**, y un **harness de evaluación offline** para medir calidad de recuperación y latencia.

El objetivo es acercarse a un sistema de conocimiento y soporte **serio y demostrable** (portafolio o MVP), no a un simple chat sobre PDFs sin trazabilidad.

---

## Qué hace el sistema

| Área | Descripción |
|------|-------------|
| **Ingesta** | Indexa runbooks, FAQs, documentación técnica y tickets (TXT, Markdown, PDF, JSON) en fragmentos con metadatos y embeddings. |
| **Consulta** | Recibe preguntas en lenguaje natural, opcionalmente **reescribe la consulta** para mejorar la búsqueda, recupera contexto con **pgvector** (similitud) y **BM25** (léxico), fusiona resultados y genera una respuesta **estructurada** con el modelo de lenguaje. |
| **Trazabilidad** | Las respuestas incluyen **citas** ligadas a chunks concretos; si la evidencia es insuficiente, el sistema lo indica y evita inventar. |
| **Triage** | Estima **severidad** (p. ej. baja → crítica), si el caso **requiere humano** y sugiere **siguientes pasos**, combinando reglas y, cuando aplica, el LLM. |
| **Analítica** | Persiste preguntas, trazas de recuperación, latencias y **feedback** (útil / no útil) para alimentar el panel de métricas. |
| **Evaluación** | Script de evaluación offline con dataset en JSONL: métricas tipo hit@k, precisión@k, MRR, latencias p50/p95 y comparación entre **estrategias** de recuperación. |
| **Procesamiento asíncrono** | **Celery** + **Redis** para trabajos de ingesta en segundo plano cuando se despliega el worker. |

---

## Casos de uso típicos

- Responder con base en **documentación interna** (runbooks, políticas, procedimientos).
- Orientar sobre **causas probables** y **pasos de resolución** ante fallos (auth, facturación, integraciones).
- Mostrar **evidencia y fuentes** para auditoría o escalamiento.
- Detectar consultas con **baja confianza** o incidentes que deben **escalar** a ingeniería u otro equipo.

---

## Arquitectura (resumen)

```
[ Next.js ] ──HTTP──▶ [ FastAPI ]
                         ├── Chat (rewrite → retrieve → generate → triage)
                         ├── Ingestión (parse → chunk → embed → persistir)
                         ├── Analytics (queries, trazas, feedback)
                         └── Evaluación (dataset, métricas, reportes)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        PostgreSQL       Redis          Celery worker
        + pgvector      (broker)        (ingesta async)
```

- **Recuperación híbrida**: resultados semánticos y BM25 se combinan (fusión tipo RRF + score ponderado) y se reordenan para el contexto enviado al LLM.
- **Guardrails básicos**: saneamiento de entrada, límites de tamaño y prompts que tratan el contexto recuperado como **dato**, no como instrucciones del usuario.

Detalle adicional: [docs/architecture.md](docs/architecture.md).

---

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| **Frontend** | Next.js 15, TypeScript, React, Tailwind CSS, shadcn/ui, TanStack Query |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| **Datos** | PostgreSQL 16, extensión **pgvector**, Redis |
| **Jobs** | Celery |
| **RAG / ML** | OpenAI (embeddings + chat), rank-bm25, tiktoken, pypdf |

---

## Estructura del repositorio

| Ruta | Contenido |
|------|-----------|
| `apps/api/` | API FastAPI, modelos, servicios RAG, Alembic, tests |
| `apps/web/` | Interfaz Next.js (chat, ingesta, dashboard, evaluación) |
| `data/sample_docs/` | Documentos de ejemplo para demos y seeds |
| `data/eval/` | Dataset JSONL para evaluación offline |
| `scripts/` | `seed_demo_data.py`, `reindex.py`, `run_eval.py` |
| `docs/` | Arquitectura, ingesta, retrieval, evaluación, ADRs |

---

## Requisitos

- **Docker** y **Docker Compose** (recomendado para levantar todo el stack).
- Cuenta y clave **OpenAI** (`OPENAI_API_KEY`) para embeddings y generación de respuestas.

---

## Arranque rápido (Docker)

1. **Variables de entorno**

   ```bash
   cp .env.example .env
   ```

   Edita `.env` y define como mínimo `OPENAI_API_KEY` y las credenciales de Postgres/Redis si las cambias respecto al ejemplo.

2. **Levantar servicios** (Postgres, Redis, API, worker, web):

   ```bash
   docker compose up --build
   ```

   La API aplica migraciones de Alembic al iniciar.

3. **Datos de demostración** (opcional, crea documentos de ejemplo con embeddings):

   ```bash
   docker compose exec api python scripts/seed_demo_data.py
   ```

4. **URLs**

   | Servicio | URL por defecto |
   |----------|-----------------|
   | Interfaz web | http://localhost:3000 |
   | API REST | http://localhost:8000 |
   | Documentación interactiva (OpenAPI) | http://localhost:8000/docs |

---

## Desarrollo sin Docker (referencia)

- **Backend:** entorno Python 3.12, `cd apps/api`, instalar `requirements/dev.txt`, configurar `.env` con `POSTGRES_HOST=localhost`, ejecutar `alembic upgrade head` y `uvicorn app.main:app --reload`.
- **Frontend:** `cd apps/web`, `npm ci`, `npm run dev` (variable `NEXT_PUBLIC_API_URL` apuntando a la API).

---

## Scripts y utilidades

| Comando | Uso |
|---------|-----|
| `make dev` | Equivale a `docker compose up --build`. |
| `python scripts/seed_demo_data.py` | Carga documentos de muestra con IDs estables (útil junto al dataset de eval). |
| `python scripts/reindex.py` | Reconstruye chunks y embeddings para documentos ya existentes. |
| `python scripts/run_eval.py` | Ejecuta evaluación offline; genera informes bajo `artifacts/` y registra una corrida en la base. |

---

## Tests y calidad

| Ámbito | Comando |
|--------|---------|
| Tests unitarios API | `cd apps/api && pytest -m "not integration"` |
| Lint / build frontend | `cd apps/web && npm run lint && npm run build` |
| E2E (Playwright) | `cd apps/web && npm run test:e2e` |

Integración continua: [.github/workflows/ci.yml](.github/workflows/ci.yml).

---

## Documentación adicional

- [Arquitectura](docs/architecture.md) — visión general y diagrama.
- [Ingesta](docs/ingestion.md) — formatos y pipeline.
- [Recuperación](docs/retrieval.md) — estrategias semántica, BM25 e híbrida.
- [Evaluación](docs/evaluation.md) — métricas y ejecución del runner.
- [Ejemplos de API](docs/api_examples.md) — payloads típicos.
- [Guion de demo](docs/demo_script.md) — pasos sugeridos para una demo.
- [Decisiones (ADRs)](docs/decisions/) — decisiones de diseño breves.

---

## Licencia

Proyecto de referencia / portafolio: añade la licencia que corresponda a tu uso (MIT, propia, etc.).
