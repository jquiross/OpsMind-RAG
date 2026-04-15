# Demo rápida

1. `cp .env.example .env` y define `OPENAI_API_KEY`.
2. `docker compose up --build`.
3. `docker compose exec api python scripts/seed_demo_data.py` (requiere `OPENAI_API_KEY` para embeddings).
4. Abre `http://localhost:3000`, pestaña Chat, pregunta del dataset eval.
5. Revisa citas en el panel lateral y feedback thumbs.
6. Dashboard en `/dashboard`.

Los scripts y `data/sample_docs` se copian en la imagen de la API para poder ejecutar el seed dentro del contenedor.
