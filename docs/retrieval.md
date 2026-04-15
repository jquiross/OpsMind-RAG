# Recuperación

Estrategias expuestas en `HybridRetriever.retrieve`:

- `semantic_only`: orden por distancia coseno en pgvector.
- `bm25_only`: BM25 (`rank_bm25`) sobre tokens del contenido.
- `hybrid_rerank`: fusión RRF de listas semántica y léxica + score `w_sem * sem + w_lex * lex` con pesos en `Settings`.

La reescritura de consulta (`query_rewrite`) usa el LLM para mejorar el embedding de búsqueda sin sustituir la pregunta del usuario en la respuesta final.
