from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.document import Document
from app.schemas.ingest import DocumentOut

router = APIRouter()


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentOut]:
    docs = db.scalars(select(Document).order_by(Document.created_at.desc())).all()
    return [
        DocumentOut(
            id=d.id,
            title=d.title,
            source_type=d.source_type,
            processing_status=d.processing_status,
            created_at=d.created_at.isoformat(),
        )
        for d in docs
    ]


@router.get("/documents/{document_id}")
def get_document(document_id: UUID, db: Session = Depends(get_db)) -> dict:
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": str(doc.id),
        "title": doc.title,
        "source_type": doc.source_type,
        "processing_status": doc.processing_status,
        "error_message": doc.error_message,
        "created_at": doc.created_at.isoformat(),
    }
