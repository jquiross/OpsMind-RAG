"""Re-embed all chunks for documents (simple full reindex)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

for path in (REPO_ROOT / "apps" / "api", REPO_ROOT):
    if (path / "app").is_dir():
        sys.path.insert(0, str(path))
        break

os.environ.setdefault("POSTGRES_HOST", "localhost")

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.document import Document, DocumentChunk
from app.services.ingest_service import ingest_text_as_document


def reindex_all() -> None:
    db = SessionLocal()
    try:
        docs = db.scalars(select(Document)).all()
        for d in docs:
            chunks = db.scalars(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == d.id)
                .order_by(DocumentChunk.chunk_index)
            ).all()
            if not chunks:
                continue
            full_text = "\n\n".join(c.content for c in chunks)
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == d.id))
            db.commit()
            ingest_text_as_document(
                db, title=d.title, text=full_text, source_type=d.source_type, document_id=d.id
            )
        print(f"Reindexed {len(docs)} documents.")
    finally:
        db.close()


if __name__ == "__main__":
    reindex_all()
