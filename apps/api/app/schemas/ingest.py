from uuid import UUID

from pydantic import BaseModel


class IngestResponse(BaseModel):
    document_id: UUID
    status: str
    message: str | None = None


class DocumentOut(BaseModel):
    id: UUID
    title: str
    source_type: str
    processing_status: str
    created_at: str

    model_config = {"from_attributes": True}
