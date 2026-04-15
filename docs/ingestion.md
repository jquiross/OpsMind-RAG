# Ingesta

Formatos soportados: `txt`, `md`, `pdf`, `json` (tickets).

1. Parseo y normalización de texto (`app/rag/ingest/`).
2. Chunking con tiktoken (~512 tokens, solapamiento ~80).
3. Embeddings `text-embedding-3-small` y persistencia en `document_chunks.embedding`.
4. Reindexación: `python scripts/reindex.py` o reemplazo de chunks vía `ingest_text_as_document` con `document_id` existente.
