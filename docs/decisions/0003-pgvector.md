# ADR 0003 — pgvector

- Los embeddings se almacenan en PostgreSQL con el tipo `vector(1536)` y distancia coseno en consultas.
- Evita un segundo almacén vectorial; simplifica despliegue y backups.
