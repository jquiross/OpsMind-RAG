from pathlib import Path

from app.db.session import SessionLocal
from app.services.ingest_service import ingest_file
from app.workers.celery_app import celery_app


@celery_app.task(name="opsmind.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="opsmind.ingest_file")
def ingest_file_task(path: str, title: str | None = None) -> str:
    db = SessionLocal()
    try:
        doc = ingest_file(db, Path(path), title=title)
        return str(doc.id)
    finally:
        db.close()
