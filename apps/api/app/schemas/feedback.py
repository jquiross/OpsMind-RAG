from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    query_id: UUID
    rating: int = Field(ge=-1, le=1)
    comment: str | None = Field(default=None, max_length=2000)
