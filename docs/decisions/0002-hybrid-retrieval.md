# ADR 0002 — Recuperación híbrida

- Combinamos búsqueda semántica (densidad de significado) con BM25 (coincidencia léxica de términos poco frecuentes).
- Fusión: Reciprocal Rank Fusion + score híbrido ponderado; sin cross-encoder en MVP (rerank = orden por score fusionado).
