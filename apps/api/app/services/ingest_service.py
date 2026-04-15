from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk, ProcessingStatus, SourceType
from app.rag.embeddings import embed_texts
from app.rag.ingest.chunker import chunk_text
from app.rag.ingest.parsers import parse_md, parse_pdf, parse_ticket_json, parse_txt
from app.rag.ingest.normalize import normalize_text


def _checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ingest_file(db: Session, path: Path, title: str | None = None) -> Document:
    suffix = path.suffix.lower().lstrip(".")
    if suffix == "txt":
        text, meta = parse_txt(path)
        st = SourceType.TXT.value
    elif suffix == "md":
        text, meta = parse_md(path)
        st = SourceType.MD.value
    elif suffix == "pdf":
        text, meta = parse_pdf(path)
        st = SourceType.PDF.value
    elif suffix == "json":
        text, meta = parse_ticket_json(path)
        st = SourceType.TICKET_JSON.value
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    raw_bytes = path.read_bytes()
    checksum = _checksum(raw_bytes)
    doc_title = title or path.name

    doc = Document(
        title=doc_title,
        source_type=st,
        source_path=str(path),
        checksum=checksum,
        processing_status=ProcessingStatus.PROCESSING.value,
    )
    db.add(doc)
    db.flush()

    meta_full = {"source_type": st, **meta}
    chunks = chunk_text(text, doc_metadata=meta_full)
    texts = [c.content for c in chunks]
    embeddings = embed_texts(texts)

    for ch, emb in zip(chunks, embeddings, strict=True):
        db.add(
            DocumentChunk(
                id=uuid.uuid4(),
                document_id=doc.id,
                chunk_index=ch.chunk_index,
                content=ch.content,
                token_count=ch.token_count,
                metadata_json={**ch.metadata, **meta_full},
                embedding=emb,
            )
        )

    doc.processing_status = ProcessingStatus.COMPLETED.value
    db.commit()
    db.refresh(doc)
    return doc


def ingest_text_as_document(
    db: Session,
    *,
    title: str,
    text: str,
    source_type: str = "txt",
    document_id: uuid.UUID | None = None,
) -> Document:
    text = normalize_text(text)
    checksum = _checksum(text.encode("utf-8"))
    if document_id and (existing := db.get(Document, document_id)):
        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
        existing.title = title
        existing.source_type = source_type
        existing.checksum = checksum
        existing.processing_status = ProcessingStatus.PROCESSING.value
        doc = existing
    else:
        doc = Document(
            id=document_id or uuid.uuid4(),
            title=title,
            source_type=source_type,
            source_path=None,
            checksum=checksum,
            processing_status=ProcessingStatus.PROCESSING.value,
        )
        db.add(doc)
    db.flush()
    chunks = chunk_text(text, doc_metadata={"source_type": source_type})
    embeddings = embed_texts([c.content for c in chunks])
    for ch, emb in zip(chunks, embeddings, strict=True):
        db.add(
            DocumentChunk(
                document_id=doc.id,
                chunk_index=ch.chunk_index,
                content=ch.content,
                token_count=ch.token_count,
                metadata_json=ch.metadata,
                embedding=emb,
            )
        )
    doc.processing_status = ProcessingStatus.COMPLETED.value
    db.commit()
    db.refresh(doc)
    return doc
