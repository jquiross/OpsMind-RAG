from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CitationSchema(BaseModel):
    document_title: str
    chunk_id: str


class TriageSchema(BaseModel):
    severity: str
    needs_human: bool
    confidence: float
    reasoning_summary: str
    suggested_next_steps: list[str] = Field(default_factory=list)
    label: str = ""


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    retrieval_strategy: str = Field(default="hybrid_rerank")
    use_query_rewrite: bool = True


class ChatResponse(BaseModel):
    summary: str
    probable_cause: str
    suggested_steps: list[str]
    confidence: float
    needs_human: bool
    severity: str
    citations: list[CitationSchema]
    triage: TriageSchema
    query_id: UUID
    rewritten_query: str | None = None
    insufficient_evidence: bool = False
    injection_signals: list[str] = Field(default_factory=list)
    raw_json: dict[str, Any] | None = None
