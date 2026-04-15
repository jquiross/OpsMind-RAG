from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ingest import IngestResponse
from app.services.ingest_service import ingest_file

router = APIRouter()


@router.post("/ingest/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IngestResponse:
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    dest = upload_dir / safe_name
    content = await file.read()
    dest.write_bytes(content)
    try:
        doc = ingest_file(db, dest, title=file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return IngestResponse(document_id=doc.id, status=doc.processing_status, message="indexed")
